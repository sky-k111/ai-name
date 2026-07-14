<template>
  <div class="name-gallery">
    <RecommendedNameCard
      v-if="names[0]"
      :name="names[0]"
      :index="0"
      variant="featured"
      @favorite="emit('favorite', $event)"
      @detail="openDetail(names[0], 0)"
    />
    <div v-if="names.length > 1" class="name-gallery__columns">
      <RecommendedNameCard
        v-for="(name, index) in names.slice(1)"
        :key="name.full_name"
        :name="name"
        :index="index + 1"
        variant="compact"
        @favorite="emit('favorite', $event)"
        @detail="openDetail(name, index + 1)"
      />
    </div>
    <NameDetailSheet
      v-if="selected"
      :key="selected.name.full_name"
      :name="selected.name"
      :index="selected.index"
      @close="selected = null"
    />
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import type { FavoriteAction, NameItem } from "../types";
import NameDetailSheet from "./NameDetailSheet.vue";
import RecommendedNameCard from "./RecommendedNameCard.vue";

defineProps<{ names: NameItem[] }>();
const emit = defineEmits<{ favorite: [action: FavoriteAction] }>();
const selected = ref<{ name: NameItem; index: number } | null>(null);
function openDetail(name: NameItem, index: number) { selected.value = { name, index }; }
</script>

<style scoped>
.name-gallery { display: grid; gap: 18px; }
.name-gallery__columns { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); align-items: start; gap: 18px; }
@media(max-width:760px){.name-gallery__columns{grid-template-columns:1fr}}
</style>
