<template>
    <b-container>
        <b-row>
            <b-col cols=10>
                <svg id="svg" :viewBox="`0 0 ${width} ${width}`">
                    <g id="sunburst" :transform="`translate(${width / 2},${width / 2})`">
                    </g>
                </svg>
            </b-col>
            <b-col cols=2>
                <h6>Trade Value<br>max relative <br>to section</h6>
                <div id="legend" class="d-inline-block">
                </div>
            </b-col>
        </b-row>
    </b-container>
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
            title: undefined as unknown as d3.Selection<d3.BaseType, unknown, HTMLElement, any>
        }
    },
    methods: {
        partition() {
            //prepara los datos segun dummy_val
            const root = d3.hierarchy(this.data).sum(d => (!d.children)?d.dummy_val:undefined).sort((a, b) => b.value! - a.value!);
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
        wrap(text, width) {
            text.each(function () {
                var text = d3.select(this),
                    words = text.text().split(/\s+/).reverse(),
                    word = '',
                    line = [],
                    lineNumber = 0,
                    lineHeight = 1, // ems
                    y = text.attr("y")-((words.length+1)*4),
                    dy = parseFloat(text.attr("dy")),
                    tspan = text.text(null).append("tspan").attr("x", 0).attr("y", y).attr("dy", dy + "em");
                while (word!=undefined) {
                    word = words.pop();
                    line.push(word);
                    tspan.text(line.join(" "));
                    if (tspan.node().getComputedTextLength() > width) {
                        line.pop();
                        tspan.text(line.join(" "));
                        line = [word];
                        tspan = text.append("tspan").attr("x", 0).attr("y", y).attr("dy", ++lineNumber * lineHeight + dy + "em").text(word);
                    }
                }
            });
        },
        clicked(event: any, p: d3.HierarchyRectangularNode<unknown>){
            this.parent.datum(p.parent || this.root);

            //cambia el color del padre
            this.parent.attr("fill", this.color(p.data.color));

            //cambia el titulo del padre
            this.title.style("fill", p.data.color>=0.6?"white":"black").text(p.data.name);

            //no se que hace esto pero dejelo aqui xd
            //posiblemente haga la transicion entre los elementos del siguiente nivel al nivel actual para visualizarlos
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
            }).attr("fill-opacity", d => self.arcVisible(d.target) ? 1 : 0)
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
        //Sunburst chart
        const format = d3.format(",d")
        this.root = this.partition();
        this.root.each((d: any) => d.current = d);
        this.descendants = this.root.descendants().slice(1);
        this.g = select("#sunburst");
        //genera los slices
        this.path = this.g
            .append("g")
            .selectAll("path")
            .data(this.descendants)
            .join("path")
            .attr("fill", d => this.color(d.data.color)) //define color
            .attr("fill-opacity", d => this.arcVisible(d.current) ? (d.children ? 1 : 1) : 0) //define visibilidad, si se muestra o no
            .attr("d", d => this.arc(d.current)); //dibuja el arco

        this.path.filter(d => d.children).style("cursor", "pointer").on("click",this.clicked); //clickeable si tiene hijos

        //agrega los titulos del hover
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
            .attr("fill-opacity", d => +this.labelVisible(d.current)) //define visibilidad, si se muestra o no
            .attr("transform", d => this.labelTransform(d.current)) //coloca la label donde corresponde
            .text(d => d.data.name) //texto del label
            .style("fill", d => d.data.color>=0.6?"white":"black") //color del texto
            .call(this.wrap,7*20); //wrap del texto

        //elemento padre
        this.parent = this.g
            .append("circle")
            .datum(this.root)
            .attr("r", this.radius) //radio del circulo
            .attr("fill", d => this.color(d.data.color)) //color
            .attr("pointer-events", "all")
            .on("click", this.clicked);

        //label del elemento padre observado
        this.title = select("#svg").append("text")
            .attr("id","title")
            .attr("x",(this.width/2)) //posicion en el centro
            .attr("y",(this.width/2)) //posicion en el centro
            .attr("text-anchor","middle")
            .style("fill", this.root.data.color>=0.6?"white":"black") //color
            .text(this.root.data.name);

        //Colorscale bar
        const vh = Math.max(document.documentElement.clientHeight || 0, window.innerHeight || 0);
        const legendHeight = vh*0.7;
        const legendWidth = 80;
        const margin = {top: 10, right: 60, bottom: 10, left: 2};

        //barra de color
        const canvas = d3.select("#legend")
            .style("height", legendHeight + "px")
            .style("width", legendWidth + "px")
            .style("position", "relative")
            .append("canvas")
            .attr("height", legendHeight - margin.top - margin.bottom)
            .attr("width", 1)
            .style("height", (legendHeight - margin.top - margin.bottom) + "px")
            .style("width", (legendWidth - margin.left - margin.right) + "px")
            .style("border", "1px solid #000")
            .style("position", "absolute")
            .style("top", (margin.top) + "px")
            .style("left", (margin.left) + "px")
            .node();

        const ctx = canvas?.getContext("2d");

        //escala de color continua
        const colorScale = d3.scaleSequential().domain([0,1]).interpolator(d3.interpolateYlOrRd);

        //escala de la leyenda
        const legendScale = d3.scaleLinear().range([1,legendHeight - margin.top - margin.bottom]).domain(colorScale.domain());

        //parte de la barra tambien
        const image = ctx?.createImageData(1, legendHeight - margin.top - margin.bottom);
        d3.range(legendHeight).forEach(function(i) {
            var c = d3.rgb(colorScale(legendScale.invert(i)));
            image!.data[4*i] = c.r;
            image!.data[4*i + 1] = c.g;
            image!.data[4*i + 2] = c.b;
            image!.data[4*i + 3] = 255;
        });
        ctx?.putImageData(image!, 0, 0);

        //leyenda con escala indicada de 0.1 en 0.1 del 0 al 1.
        const legendAxis = d3.axisRight(legendScale).tickSize(6).ticks(10);
        const svg = d3.select("#legend")
            .append("svg")
            .attr("height", legendHeight + "px")
            .attr("width", (legendWidth) + "px")
            .style("position", "absolute")
            .style("left", "0px")
            .style("top", "0px")

        svg
            .append("g")
            .attr("class", "axis")
            .attr("transform", "translate(" + (legendWidth - margin.left - margin.right + 3) + "," + (margin.top) + ")")
            .call(legendAxis);
    }   
});
</script>

<style>
    text {
        fill: black;
        font-size: 13px;
        pointer-events: none;
        text-anchor: middle;
        word-wrap: break-word;
    }

    h6 {
        color: black;
        font-size: 13px;
    }
</style>
