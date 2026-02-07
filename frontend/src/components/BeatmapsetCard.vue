<template>
    <div class="card">
        <div
            class="thumb"
            :style="{ backgroundImage: thumbnailStyle }"
            aria-hidden="true"  
        >
        <img class="cover-image" v-if="props.beatmapset.cover_card" :src="props.beatmapset.cover_card" alt="Cover image" />
        </div>

        <div class="info">
            <div class="title-row">

                <h3 class="title">{{ props.beatmapset.title }}</h3>
                <div class="rating" v-if="props.beatmapset.star_rating || props.beatmapset.rating">
                    <span class="star">★</span>
                    <span class="val">{{ props.beatmapset.star_rating || props.beatmapset.rating }}</span>
                </div>
            </div>

            <p class="creator">mapped by <strong>{{ props.beatmapset.creator }}</strong></p>

            <div class="meta-row">
                <span class="tag" v-if="props.beatmapset.source">{{ props.beatmapset.source }}</span>
            </div>

            <div class="actions">
                <button class="btn ghost" @click.stop="openSet">Open</button>
            </div>
        </div>
    </div>
</template>

<script setup>
// BeatmapsetCard.vue — richer visual card
const props = defineProps({
    beatmapset: { type: Object, required: true }
})

const thumbnailStyle = (() => {
    const url = props.beatmapset.cover_url || props.beatmapset.thumb || props.beatmapset.background || ''
    return url ? `url('${url}')` : 'none'
})()

function openSet() {
    const id = props.beatmapset.id
    if (id) {
        window.open(`https://osu.ppy.sh/beatmapsets/${id}`, '_blank')
    }
}
</script>

<style scoped>
.card {
    display: flex;
    align-items: stretch;
    background: linear-gradient(180deg, #ffffff 0%, #fbfdff 100%);
    border-radius: 10px;
    box-shadow: 0 6px 18px rgba(15, 23, 42, 0.08);
    overflow: hidden;
    transition: transform 180ms ease, box-shadow 180ms ease;
}
.card:hover {
    box-shadow: 0 14px 40px rgba(15, 23, 42, 0.14);
}

.thumb {
    width: 160px;
    min-width: 160px;
    background-size: cover;
    background-position: center;
    position: relative;
}
.thumb::after {
    content: '';
    position: absolute;
    inset: 0;
    background: linear-gradient(180deg, rgba(0,0,0,0.0) 30%, rgba(0,0,0,0.28) 100%);
}

.cover-image {
    width: 100%;
    height: 100%;
    object-fit: cover;
    display: block;
}

.info {
    padding: 12px 16px;
    display: flex;
    flex-direction: column;
    gap: 8px;
    flex: 1 1 0;       /* Allow shrinking */
    min-width: 0;      /* Critical for nested truncation */
    overflow: hidden;  /* Contain children */
}
.title-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    min-width: 0; /* Allow flex children to shrink below content size */
}
.title {
  margin: 0;
  font-size: clamp(14px, 1vw, 18px);
  font-weight: 700;
  color: #0f1724;
  flex: 1 1 0;       /* Allow shrinking */
  min-width: 0;      /* Critical: override min-width: auto */
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.rating {
    display: flex;
    align-items: center;
    gap: 4px;
    background: rgba(255,255,255,0.9);
    padding: 4px 8px;
    border-radius: 999px;
    font-weight: 700;
    color: #111827;
    box-shadow: 0 2px 6px rgba(2,6,23,0.06);
}
.rating .star { color: #f6c85f }
.creator { margin: 0; color: #374151; font-size: 0.95rem }
.status { color: #6b7280; font-size: 0.86rem }

.meta-row { display:flex; gap:8px; align-items:center; }
.tag {
    background: rgba(34,197,94,0.12);
    color: #065f46;
    padding: 4px 8px;
    font-size: 0.78rem;
    border-radius: 999px;
}

.actions { margin-top: auto; display:flex; gap:8px }
.btn { border: none; padding: 8px 12px; border-radius: 8px; font-weight: 600; text-decoration:none; display:inline-flex; align-items:center; gap:8px }
.btn.ghost { background: transparent; color: #0f1724; box-shadow: inset 0 0 0 1px rgba(15,23,36,0.06); cursor: pointer;}
.btn.primary { background: #2563eb; color: white }

@media (max-width: 720px) {
    .card { flex-direction: row; }
    .thumb { width: 110px; height: 90px }
}

</style>