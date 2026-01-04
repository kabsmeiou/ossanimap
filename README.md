# ossanimap

ossanimap is an osu! beatmapset packager that aggregates ranked/loved osu! beatmaps into downloadable packages grouped by the anime name.

### Why create ossanimap?

ossanimap is created to simplify the process of searching and downloading the songs from the anime series you love! It fetches all the ranked maps associated with the anime name and bundles them into a downloadable artifact. 

### Who is ossanimap for?

ossanimap is for those who want to save time downloading all the songs from an anime series, especially long running ones with lots of OSTs. It is mainly for me!


### Public-facing System Features: (bolded are core features)

Download beatmap package
Search beatmap package
Request anime (?)
Filter for maptype (standard, taiko, mania, catch)

### Backend Logic: Collection Process

Provided a set of anime names, the system will fetch for the anime metadata from api.animethemes.moe and collect it.
Upon collection, the anime title from the metadata is used to search for beatmapsets from an osu! mirror: chimu.moe
With the fixed filter of ranked=1 and anime title enclosed in quotation marks(e.g “bakemonogatari”), the search is executed
After the search, the json object is reconciled with a backend model Beatmapset to prepare for processing. At this stage, it will be a list of beatmapsets.
The id is then collected for each beatmapsets and a Pack object is created and saved to the database along with an auto-generated Pack name, anime title, etc. This is defined in schemas/pack.py
The pack will be available in the routes at this point and is ready to be downloaded



### Backend Logic: Download Process

the pack_ids will be downloaded individually using chimu.moe’s download api from the user's browser
Due to the rate limits, downloads shall be monitored and stopped before it goes past the rate.
