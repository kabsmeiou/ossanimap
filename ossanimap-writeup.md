# ossanimap: an osu! beatmap packager for anime soundtracks


## Why I started this project

I started this side project just before then new year starts, having finished the deployment setup of another project and wanting to work on something new. I happened to play some osu! before going back to my family's place and thought about beatmap packs. I really liked the OSTs of this one anime I binged over the holidays and wanted to play all the songs it has. Of course, I can simply just search for the name and click one by one but I am a lazy person and a question occured to me: what if I can just create beatmap packs featuring the anime that I want? Well, since I was already familiar with beatmap mirrors like beatconnect.io and chimu.moe, all I had to do was verify the availability of their APIs and get started with the development. 

## Development

For the backend of the system, I decided to use Python with FastAPI. I considered using Nextjs but I just thought it felt right to use Python for tasks relating to data processing. I was assuming at this stage that I'll be dealing with a bunch of data stuff. Well, fast-forward to the initial stages of development but it was more on making the external API calls faster and learning SQLAlchemy as I go.

### Task 1: Creating the schemas

One of the things I realized while working with this project is the fact that schemas and models are different things. **Models** are generally used to refer to the contract between the server and the database while **Schemas** are contracts between the client and the server. I used to treat them as the same! Anyway, my first approach was creating the schemas(during the inital creation, I still thought they're models). For this, I went through the documentation of the APIs (chimu.moe & animethemes) that I am going to use. Initially, I copied every single field for each object but while going through one of the objects with about 20 fields, I wondered, worried about the payload: "Do I really have to put all these fields just to receive the data and use like 5 of them?". My stupid ass learned that you really don't have to include every field, just the ones you need. With this epiphany, the task went from matching to deciding which fields matter to my system. With careful consideration of the current needs and future possibilities, I ended up with the following:

```python
# animethemes API response schema
class Anime(BaseModel):
    """
    Represents anime metadata from animethemes.moe API.
    """
    id: int = Field(..., description="Unique anime identifier")
    name: str = Field(..., description="Name of the anime")
    slug: str = Field(..., description="Slug identifier for the anime")
    synopsis: Optional[str] = Field(None, description="Synopsis of the anime")
    image_link: Optional[str] = Field(None, description="Link to the anime image")
```

```python
class Beatmapset(BaseModel):
    id: int = Field(..., description="beatmapset id")
    artist: str = Field(..., description="artist")
    availability: Availability = Field(..., description="availability")
    beatmaps: List[Beatmap] = Field(..., description="beatmaps in the beatmapset")
    genre: Any = Field(..., description="genre")
    nsfw: bool = Field(..., description="if the beatmapset contains NSFW")
    source: str = Field(..., description="source")
    status: str = Field(..., description="status")
    title: str = Field(..., description="title")
    title_unicode: str = Field(..., description="title in unicode")
    track_id: Optional[int] = Field(None, description="track_id")
    play_count: int = Field(..., description="number of plays")
    favourite_count: int = Field(..., description="number of favourites")
```

Great. Some of these fields aren't being used yet but they're mostly fields that I think I might want to use later on and simply just added it there like for example, I can use the *nsfw* field for filtering purposes for users or the *genre* could be displayed along with the beatmap pack details, you get the idea. With the external APIs out of the way, its time to decide for the beatmap pack schema or **Pack**.

Obviously, it's important to consider the system features when creating this schema:
1. I want the pack to have multiple maps
2. I want the users to be able to request the creation of packs based on an anime they input
3. I want to be able to count the downloads of a pack
4. I want the pack to show some information about the anime

From these, I can easily figure out what I need: a list of beatmap ids, the anime title of the pack, download count, and some additional anime-related metadata. Along with some extra fields like dates and for future updates, the schema below is what I created:

```python
class Pack(BaseModel):
    """
    Represents a collection of osu! beatmapsets grouped by anime.
    """
    id: int = Field(..., description="Unique pack identifier")
    name: str = Field(..., description="Human-readable pack name")
    anime_title: str = Field(..., description="Title of the anime")
    image_link: Optional[str] = Field(default=None, description="Link to the anime image")
    status: List[int] = Field(..., description="status of beatmap in the pack: 1=ranked,2=loved")
    mode: List[int] = Field(..., description="modes of beatmap in the pack: -1=all,0=standard,1=taiko,2=catch,3=mania")
    synopsis: Optional[str] = Field(default=None, description="Brief synopsis of the anime")
    beatmapset_ids: List[int] = Field(..., description="List of beatmapset IDs in this pack")
    beatmapset_count: int = Field(..., description="Total number of beatmapsets")
    downloads: int = Field(default=0, description="Number of times this pack has been downloaded")
    created_at: Optional[str] = Field(..., description="ISO 8601 timestamp of pack creation")
    updated_at: Optional[str] = Field(..., description="ISO 8601 timestamp of last update")
```
With the schema finished I went on to implement the logic.

### Task 2: Implementation of the logic

<!-- to insert some diagram/chart here for the processes -->

To get started with the implementation, I first dealt with the easier ones. That is, the function for fetching anime metadata from *animethemes* and the function for searching for beatmaps with chimu.moe. 

These were fairly easy, it was harder to figure out the parameters I can use for chimu.moe because it wasn't in the documentation. I had to join the discord server to see how other people queried. Aside from this, it was a swift phase for the MVP. I needed only a search_beatmapset() and a get_anime_metadata(). Later on however, I faced an several issues related to these external API calls. 

First, they can be slow! It can be client-side network problems, the server of the API, and many more but they can be slow and that is a problem because it can block other processes if we keep waiting for the API response. I addressed this with async setups and I talked about it [below](#task-5-using-async). The other problem is **consistency**. Since users can request for packs, they can type in the anime title and perform the backend processes to fetch metadata and search for beatmapsets. But that would only work if the anime title is correct in the first place. Both in spelling, and the actual anime they're referring to. Doing manual reconciliation with some algorithm is too much so to work with this, I decided to sacrifice some response time by using the *animethemes* search api! 

```python
    # step 1 is to fetch anime metadata but the creation process
    # already obtains the needed info so we just pass it directly
    # from the client
    beatmapsets = await self._search_beatmapsets(anime.name, status, mode)
    beatmapset_ids = self._extract_beatmapset_ids(beatmapsets)
    pack: PackCreate = self._create_pack(
        anime=anime,
        beatmapset_ids=beatmapset_ids,
        mode=mode,
        status=status,
    )
```

The idea is that when clients types in their anime, I can send a request for search in the backend and the server returns the *top_k* results for the users to choose from. This way. I don't need to worry about typos and animes that doesn't exist. But at the cost of extra latency(the request)! To make up for it, I removed the process of fetching the metadata and instead sends it from the client, making use of the fact that it was already fetched with the search function.

### Task 3: Implementing the routes

Bringing my learnings from my earlier projects, I wrote the routes to have as little business logic as possible. Also, in deciding what routes to build, I simply thought about what database operations or services do I need to allow my users to use. There is not much going on in the implementation of this because all of the logic being executed inside the routes are abstracted away with functions. For routes handling database operations, however, I decided to use the Depends() function to handle the async session required to interact with the database. With this, the session lasts for the duration of the request, is properly scoped (because they are not supposed to be global), and should close everytime. There is one exception to this: the *create_packs* route. This is due to the fact that the db transaction happens as a job for a worker to finish. In the first place, its not possible to serialize the session object and so it cannot be stored in the job queue.

### Task 4: Setting up models
Now, for the models! It's all about choosing the fields that matters, the ones that we want to store and will be accessed most of the time. In this case, we care for the fields for pack and anime, assuming that pack includes the ids that we need from the beatmapsets. With these fields, we want to reduce the amount of external API calls needed for requests that are used the most. Given this, it becomes a simple task!

### Task 5: Using Async 
bump
### Task 6: Inserting error logs

## What's next?
