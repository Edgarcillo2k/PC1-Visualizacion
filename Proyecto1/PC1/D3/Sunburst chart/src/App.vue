<template>
    <div id="app">
        <input type="file" @change="readJSON">
        <SunburstChart :data="data" v-if="data"/>
    </div>
</template>

<script lang="ts">
import Vue from 'vue';
import IcicleChart from './components/IcicleChart.vue';
import SunburstChart from './components/SunburstChart.vue';
import * as d3 from 'd3';

export default Vue.extend({
    name: 'App',
    components: {
        SunburstChart
    },
    data(){
        return {
            data: undefined as any
        }
    },
    methods: {
        readJSON(evt: any) {
            const file = evt.target.files[0];
            const reader = new FileReader();
            reader.onload = (e) => {
                // Cuando el archivo se terminó de cargar
                if(e.target!=null)
                    this.data = JSON.parse(e.target.result as string);
            };
            reader.readAsText(file);
        },
    }
});
</script>

<style>
#app {
    font-family: Avenir, Helvetica, Arial, sans-serif;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    text-align: center;
    color: #2c3e50;
    margin-top: 60px;
}
</style>
