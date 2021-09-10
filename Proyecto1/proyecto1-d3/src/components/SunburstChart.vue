<template>
    <div>
        <svg :viewBox="`0 0 ${width} ${width}`">
            <g :transform="`translate(${width / 2},${width / 2})`">
                <!--<path v-for="(item,i) in descendants" :key="i" :fill="color(item.data.color)" :d="arc(item.current)" :fill-opacity="arcVisible(item.current) ? (item.children ? 1 : 1) : 0" @click="clicked(item.current)"/>
                <g pointer-events="none" text-anchor="middle">
                    <text v-for="(item, i) in descendants" :key="i" :transform="labelTransform(item.current)" :fill-opacity="+labelVisible(item.current)" :class="$style.label">
                        {{ item.data.name }}
                    </text>
                </g>
                <circle :r="radius" :fill="color(1)" pointer-events="all" @click="clicked(undefined)"/>-->
            </g>
        </svg>
    </div>
</template>

<script lang="ts">
import Vue from 'vue';
import * as d3 from 'd3';
import { select } from 'd3';

export default Vue.extend({
    name: 'SunburstChart',
    props: {
        data: Object
    },
    data() {
        return {
            root: undefined as unknown as d3.HierarchyRectangularNode<unknown>,
            descendants: [] as d3.HierarchyRectangularNode<unknown>[],
            width: window.innerHeight, //tamanio de la ventana
            radius: window.innerHeight/5,
            g: undefined as unknown as d3.Selection<d3.BaseType, unknown, HTMLElement, any>,
            path: undefined as unknown as d3.Selection<d3.BaseType, d3.HierarchyRectangularNode<unknown>, d3.BaseType, unknown>,
            labels: undefined as unknown as d3.Selection<d3.BaseType, d3.HierarchyRectangularNode<unknown>, d3.BaseType, unknown>,
            parent: undefined as unknown as d3.Selection<SVGCircleElement, d3.HierarchyRectangularNode<unknown>, HTMLElement, any>,
        }
    },
    methods: {
        partition() {
            //prepara los datos segun dummy_val
            const root = d3.hierarchy(this.data).sum(d => d.dummy_val).sort((a, b) => b.value! - a.value!);
            return d3.partition().size([2 * Math.PI, root.height + 1])(root);
        },
        arc(d: d3.HierarchyRectangularNode<unknown>) {
            //forma los arcos (los slices de colores) y los ubica en la posicion correspondiente
            const arc = d3.arc()
                .startAngle(d.x0)
                .endAngle(d.x1)
                .padAngle(Math.min((d.x1 - d.x0) / 2, 0.005))
                .padRadius(this.radius*1.5)
                .innerRadius(d.y0*this.radius)
                .outerRadius(Math.max(d.y0 * this.radius, d.y1 * this.radius - 1));
            // eslint-disable-next-line
            return arc();
        },
        labelTransform(d: d3.HierarchyRectangularNode<unknown>) {
            //coloca las labels en la posicion adecuada
            const x = (d.x0 + d.x1) / 2 * 180 / Math.PI;
            const y = (d.y0 + d.y1) / 2 * this.radius;
            return `rotate(${x - 90}) translate(${y},0) rotate(${x < 180 ? 0 : 180})`;
        },
        color(value: number){
            //define la escala de color de amarillo a rojo en el dominio de 0 a 1
            //saca el color correspondiente segun los valores entre 0 y 1
            const color = d3.scaleSequential().domain([0,1]).interpolator(d3.interpolateYlOrRd)(value);
            return color;
        },
        arcVisible(d: d3.HierarchyRectangularNode<unknown>) {
            //determina si un slice o arco es visible
            return d.y1 <= 2 && d.y0 >= 1 && d.x1 > d.x0;
        },
        labelVisible(d: d3.HierarchyRectangularNode<unknown>) {
            //determina si un label es visible
            return d.y1 <= 2 && d.y0 >= 1 && (d.y1 - d.y0) * (d.x1 - d.x0) > 0.03;
        },
        clicked(event: any, p: d3.HierarchyRectangularNode<unknown>){
            this.parent.datum(p.parent || this.root);
            //no se que hace esto pero dejelo aqui xd
            this.root.each(d => d.target = {
                x0: Math.max(0, Math.min(1, (d.x0 - p.x0) / (p.x1 - p.x0))) * 2 * Math.PI,
                x1: Math.max(0, Math.min(1, (d.x1 - p.x0) / (p.x1 - p.x0))) * 2 * Math.PI,
                y0: Math.max(0, d.y0 - p.depth),
                y1: Math.max(0, d.y1 - p.depth)
            });
            const t = this.g.transition().duration(750);
            // eslint-disable-next-line
            const self = this;

            //animacion de los slices de colores
            this.path.transition(t).tween("data", d => {
                const i = d3.interpolate(d.current, d.target);
                return t => d.current = i(t);
            }).filter(function(d) {
                return +this.getAttribute("fill-opacity") || self.arcVisible(d.target);
            }).attr("fill-opacity", d => self.arcVisible(d.target) ? (d.children ? 1 : 1) : 0)
                .attrTween("d", d => () => self.arc(d.current));

            //animacion de las labels    
            this.labels.filter(function(d) {
                return +this.getAttribute("fill-opacity") || self.labelVisible(d.target);
            }).transition(t)
                .attr("fill-opacity", d => +self.labelVisible(d.target))
                .attrTween("transform", d => () => self.labelTransform(d.current));
        }
    },
    mounted(){
        const format = d3.format(",d")
        this.root = this.partition();
        this.root.each((d: any) => d.current = d);
        this.descendants = this.root.descendants().slice(1);
        this.g = select("g");
        //genera los slices
        this.path = this.g
            .append("g")
            .selectAll("path")
            .data(this.descendants)
            .join("path")
            .attr("fill", d => this.color(d.data.color)) //define color
            .attr("fill-opacity", d => this.arcVisible(d.current) ? (d.children ? 1 : 1) : 0) //define visibilidad
            .attr("d", d => this.arc(d.current)); //dibuja el arco
        this.path.filter(d => d.children).style("cursor", "pointer").on("click",this.clicked);
        this.path.append("title").text(d => `${d.data.name}\nTrade Value: ${format(d.data.value)}`);
        //genera los labels
        this.labels = this.g
            .append("g")
            .attr("pointer-events", "none")
            .attr("text-anchor", "middle")
            .style("user-select", "none")
            .selectAll("text")
            .data(this.descendants)
            .join("text")
            .attr("dy", "0.15em")
            .attr("fill-opacity", d => +this.labelVisible(d.current)) //define visibilidad
            .attr("transform", d => this.labelTransform(d.current))
            .text(d => d.data.name) //texto del label
            .style("fill", d => d.data.color>=0.6?"white":"black")
        this.parent = this.g
            .append("circle")
            .datum(this.root)
            .attr("r", this.radius)
            .attr("fill", this.color(1))
            .attr("pointer-events", "all")
            .on("click", this.clicked);
    }   
});
</script>

<style>
    text {
        fill: black;
        font-size: 11px;
        pointer-events: none;
        text-anchor: middle;
        word-wrap: break-word;
    }
</style>
