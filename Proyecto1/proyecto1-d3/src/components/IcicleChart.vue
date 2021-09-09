<template>
    <div>
        <svg :heigth="height" :width="width" />
    </div>
</template>

<script lang="ts">
import Vue from 'vue';
import * as d3 from 'd3';

export default Vue.extend({
    name: 'IcicleChart',
    props: {
        data: [Object]
    },
    data(){
        return {
            height: 600,
            width: 600
        }
    },
    mounted(){
        this.create();
    },
    methods: {
        create(){
            const nodes = d3.hierarchy(this.data);
            const root = d3.partition().size([this.height,this.width])(nodes);
            console.log(root);
        }
    }
});
</script>

<style>

</style>
