<template>
  <a-card
    ref="graphCardRef"
    :title="t('knowledge.title.graph')"
    class="general-card"
  >
    <template #extra>
      <a-space>
        <div class="menu-graph">
          <a-menu mode="pop">
            <a-sub-menu key="2">
              <template #icon><icon-export></icon-export></template>
              <template #title>{{ t('knowledge.graph.export') }}</template>
              <a-menu-item key="2_0" @click="exportToPDF">{{
                t('knowledge.graph.exportToPDF')
              }}</a-menu-item>
              <a-menu-item key="2_1" @click="exportToSVG">{{
                t('knowledge.graph.exportToSVG')
              }}</a-menu-item>
              <a-menu-item key="2_2" @click="exportToPNG">{{
                t('knowledge.graph.exportToPNG')
              }}</a-menu-item>
            </a-sub-menu>
          </a-menu>
        </div>
      </a-space>
    </template>
    <div class="graph-wrapper">
      <a-spin
        :loading="loading || knowledgeStore.isAnalyzingGraph"
        style="width: 100%"
      >
        <div ref="graphContentRef" class="graph-content" />
      </a-spin>
      <div class="graph-zoom-bar-container">
        <div style="display: flex; flex-direction: column; align-items: start">
          <div class="graph-zoom-bar" style="flex-shrink: 0">
            <a-button
              :disabled="isZoomInDisabled"
              :title="t('knowledge.graph.zoomIn')"
              type="secondary"
              @click="zoomIn"
            >
              <template #icon>
                <icon-zoom-in />
              </template>
            </a-button>
            <a-button
              :disabled="isZoomOutDisabled"
              :title="t('knowledge.graph.zoomOut')"
              type="secondary"
              @click="zoomOut"
            >
              <template #icon>
                <icon-zoom-out />
              </template>
            </a-button>
            <a-button
              :disabled="false"
              :title="t('knowledge.graph.1:1')"
              type="secondary"
              @click="resetView"
            >
              <template #icon>
                <icon-original-size />
              </template>
            </a-button>
            <a-button
              :disabled="false"
              :title="t('knowledge.graph.fit')"
              type="secondary"
              @click="fitView"
            >
              <template #icon>
                <icon-fullscreen />
              </template>
            </a-button>
            <a-button
              type="secondary"
              :title="t('knowledge.operation.refresh')"
              @click="refreshGraph"
            >
              <template #icon>
                <icon-refresh />
              </template>
            </a-button>
          </div>
          <a-typography-text type="secondary" style="margin-left: 8px">
            {{ (zoomLevel.scale * 100).toFixed(0) }}%
          </a-typography-text>
        </div>
      </div>
      <div class="graph-operation-bar">
        <a-tooltip :content="t('knowledge.graph.node.type')">
          <a-select
            v-model="queryCondition.selectedNodeType"
            :style="{ width: '120px' }"
            :placeholder="t('knowledge.graph.node.type')"
            :title="t('knowledge.graph.node.type')"
          >
            <a-option
              v-for="nodeType in nodeTypes"
              :key="nodeType"
              :value="nodeType"
            >
              {{ nodeType }}
            </a-option>
          </a-select>
        </a-tooltip>
        <a-input-search
          v-model="queryCondition.searchKeyword"
          :style="{ width: '160px' }"
          :placeholder="t('knowledge.search.placeholder')"
          allow-clear
          @search="fetchData"
        />
        <a-button
          :title="t('knowledge.graph.add.node')"
          type="secondary"
          @click="addNode"
        >
          <template #icon>
            <icon-plus-circle-fill />
          </template>
        </a-button>
        <a-button
          :disabled="false"
          :title="t('knowledge.graph.add.link')"
          type="secondary"
          @click="startAddRelationship"
        >
          <template #icon>
            <icon-relation />
          </template>
        </a-button>
        <a-button
          v-if="selectedNodeRef || selectedLinkRef"
          :title="t('knowledge.operation.edit')"
          type="secondary"
          @click="editObject"
        >
          <template #icon>
            <icon-edit />
          </template>
        </a-button>
        <a-button
          v-if="
            (selectedNodeRef &&
              selectedNodeRef.type !== 'ROOT' &&
              selectedNodeRef.type !== 'SUBJECT') ||
            selectedLinkRef
          "
          :title="t('knowledge.operation.delete')"
          type="secondary"
          @click="deleteObject"
        >
          <template #icon>
            <icon-delete />
          </template>
        </a-button>
      </div>
    </div>
    <div
      v-if="showMenu"
      id="context-menu"
      :style="{
        left: contextMenuPosition.x + 'px',
        top: contextMenuPosition.y + 'px',
      }"
    >
      <ul>
        <li @click="addNode">
          <icon-plus-circle-fill />
          {{ t('knowledge.graph.add.node') }}
        </li>
        <li @click="startAddRelationship">
          <icon-relation />
          {{ t('knowledge.graph.add.link') }}
        </li>
        <li v-if="selectedNodeRef || selectedLinkRef" @click="editObject">
          <icon-edit />
          {{ t('knowledge.operation.edit') }}
        </li>
        <li
          v-if="
            (selectedNodeRef &&
              selectedNodeRef.type !== 'ROOT' &&
              selectedNodeRef.type !== 'SUBJECT') ||
            selectedLinkRef
          "
          @click="deleteObject"
        >
          <icon-delete />
          {{ t('knowledge.operation.delete') }}
        </li>
      </ul>
    </div>
  </a-card>
</template>

<script lang="ts" setup>
  import { useI18n } from 'vue-i18n';
  import * as d3 from 'd3';
  import { ref, Ref, onMounted, computed } from 'vue';
  import EventBus from '@/utils/event-bus';
  import useLoading from '@/hooks/loading';
  import {
    GraphRecord,
    NodeRecord,
    RelationshipRecord,
    queryGraph,
    deleteGraphNode,
    deleteGraphRelationship,
    addGraphNode,
    addGraphRelationship,
    updateNodeInfo,
    updateRelationshipInfo,
    queryGraphOverview,
  } from '@/api/graph';
  import html2canvas from 'html2canvas';
  import jsPDF from 'jspdf';
  import { svg2pdf } from 'svg2pdf.js';
  import { Message } from '@arco-design/web-vue';
  import { forEach } from 'lodash';
  import { useKnowledgeStore } from '@/store';

  const { t } = useI18n();

  const knowledgeStore = useKnowledgeStore();

  const knowledgeLibID = ref<number>(0);
  const subjectIDs = ref<number[] | null>(null);
  const nodeTypes = ref<string[]>([
    'ALL',
    'ROOT',
    'SUBJECT',
    'INFO',
    'PROMPT',
    'HUMAN',
    'QUESTION',
  ]);

  interface QueryCondition {
    selectedNodeType: string;
    searchKeyword: string;
  }
  const queryCondition = ref<QueryCondition>({
    selectedNodeType: 'ALL',
    searchKeyword: '',
  });
  const graphRecordData = ref<GraphRecord>({
    nodes: [],
    links: [],
    overview: {
      nodes: [],
      links: [],
    },
  });
  const graphContentRef = ref<HTMLElement | null>(null);
  const selectedNodeRef = ref<NodeRecord | null>(null);
  const selectedLinkRef = ref<RelationshipRecord | null>(null);
  const isDrawingLink = ref(false);
  const drawingLinkNode = ref<NodeRecord | null>(null);
  const zoomLevel = ref({ scale: 0.0, translateX: 0, translateY: 0 });
  const isFitingView = ref(false);
  const margin = 40; // increase margin
  const showMenu = ref(false);
  const contextMenuPosition = ref({ x: 0, y: 0 });

  const showContextMenu = (event: MouseEvent) => {
    event.preventDefault();
    event.stopPropagation();
    showMenu.value = true;
    const { clientX, clientY } = event;
    const menuHeight =
      window.document.getElementById('context-menu')?.offsetHeight || 0; // Assuming 'context-menu' is the ID
    const yPosition = clientY + menuHeight - 20; // If not enough space below, place above cursor

    const offset = graphContentRef.value?.getBoundingClientRect();
    if (offset) {
      contextMenuPosition.value = {
        x: clientX - offset.left + window.scrollX + 20,
        y: yPosition - offset.top + window.scrollY,
      };
    }
  };

  const hideContextMenu = () => {
    showMenu.value = false;
  };

  const fecthOverview = async () => {
    try {
      if (!subjectIDs.value || subjectIDs.value.length === 0) {
        if (graphRecordData.value) {
          graphRecordData.value.overview = {
            nodes: [],
            links: [],
          };
        }
        return;
      }
      const response = await queryGraphOverview(knowledgeLibID.value, {
        subjectIds: subjectIDs.value,
        type:
          queryCondition.value.selectedNodeType &&
          queryCondition.value.selectedNodeType !== 'ALL'
            ? queryCondition.value.selectedNodeType
            : null,
        content: queryCondition.value.searchKeyword,
      });
      const { data } = response;
      graphRecordData.value.overview = data;
      knowledgeStore.overview = data;
      EventBus.emit('graphSelected');
    } catch (err) {
      // Removed console statement
    }
  };

  // extract the function to get the minimum and maximum coordinates
  const getNodeCoordsMinMax = () => {
    const xValues = graphRecordData.value.nodes.map(
      (nodeRecord) => nodeRecord.x
    );
    const yValues = graphRecordData.value.nodes.map(
      (nodeRecord) => nodeRecord.y
    );

    const minX = Math.min(...xValues);
    const maxX = Math.max(...xValues);
    const minY = Math.min(...yValues);
    const maxY = Math.max(...yValues);

    return { minX, maxX, minY, maxY };
  };

  const calculateViewDimensions = () => {
    const width = graphContentRef.value?.clientWidth || 800;
    const height = 400;
    const { minX, maxX, minY, maxY } = getNodeCoordsMinMax();

    const viewWidth = maxX - minX + 2 * margin;
    const viewHeight = maxY - minY + 2 * margin;

    const scale = Math.max(
      Math.min(width / viewWidth, height / viewHeight, 1),
      0.16
    );

    const translateX = (width - viewWidth * scale) / 2 - minX * scale + margin;
    const translateY =
      (height - viewHeight * scale) / 2 - minY * scale + margin;

    return { scale, translateX, translateY };
  };

  const calculateTransform = (scale: number) => {
    const width = graphContentRef.value?.clientWidth || 800;
    const height = 400;
    const { minX, maxX, minY, maxY } = getNodeCoordsMinMax();

    const viewWidth = maxX - minX + 2 * margin;
    const viewHeight = maxY - minY + 2 * margin;

    const translateX = (width - viewWidth * scale) / 2 - minX * scale + margin;
    const translateY =
      (height - viewHeight * scale) / 2 - minY * scale + margin;

    return { translateX, translateY };
  };

  const panOffset = ref({ x: 0, y: 0 });

  function convertClientToSVG(event: MouseEvent) {
    // get the SVG element
    const svgElement = graphContentRef.value?.querySelector('svg');
    let svgRect;
    if (svgElement) {
      // get the bounding rectangle of the SVG element
      svgRect = svgElement.getBoundingClientRect();
    }
    // get the scale and panOffset from zoomLevel
    const { scale } = zoomLevel.value;
    const { x: panX, y: panY } = panOffset.value;
    let x = 0;
    let y = 0;
    if (svgRect) {
      // calculate the converted x coordinate
      x = (event.clientX - svgRect.left) / scale - panX;
      // calculate the converted y coordinate
      y = (event.clientY - svgRect.top) / scale - panY;
    }
    return { x, y };
  }

  const panGraph = (event: MouseEvent, previousMousePosition: any) => {
    if (!previousMousePosition) return { x: event.clientX, y: event.clientY };

    const dx = event.clientX - previousMousePosition.x;
    const dy = event.clientY - previousMousePosition.y;

    // Update pan offset
    panOffset.value.x += dx;
    panOffset.value.y += dy;

    // Apply transform to the graph
    const graphContent = d3.select('.graph-content svg > g');

    graphContent.attr(
      'transform',
      `translate(${zoomLevel.value.translateX + panOffset.value.x}, 
      ${zoomLevel.value.translateY + panOffset.value.y}) scale(${
        zoomLevel.value.scale
      })`
    );

    return { x: event.clientX, y: event.clientY };
  };

  const resetStyles = () => {
    d3.selectAll('.node circle')
      .attr('stroke', '#708090') // Border color
      .attr('stroke-width', 1) // Border thickness
      .attr('box-shadow', 'none');
    d3.selectAll('.link .link-visible')
      .attr('stroke', '#708090') // Border color
      .attr('stroke-width', 1)
      .attr('marker-end', 'url(#arrow)');
    d3.selectAll('.link-wrapper .link-invisible')
      .attr('stroke', 'transparent')
      .attr('stroke-width', 16);

    d3.selectAll('.node.node-drawing circle')
      .attr('stroke', '#FFAC1C') // highlight selected node
      .attr('stroke-width', 2)
      .attr('box-shadow', '2px 2px 4px rgba(0, 0, 0, 0.2)');
  };

  const markDrawingLinkNode = (node: NodeRecord) => {
    d3.select(`#node-${node.id}`)
      .attr('class', 'node node-drawing')
      .selectAll('circle')
      .attr('stroke', '#FFAC1C') // highlight selected node
      .attr('stroke-width', 2)
      .attr('box-shadow', '2px 2px 4px rgba(0, 0, 0, 0.2)');
  };

  const unmarkDrawingLinkNode = (node: NodeRecord) => {
    d3.select(`#node-${node.id}`)
      .attr('class', 'node')
      .selectAll('circle')
      .attr('stroke', '#708090') // Border color
      .attr('stroke-width', 1) // Border thickness
      .attr('box-shadow', 'none');
  };

  const tempLink: Ref<d3.Selection<
    SVGLineElement,
    unknown,
    HTMLElement,
    any
  > | null> = ref(null);

  const drawTempLink = (node: NodeRecord) => {
    // remove previous temporary link
    d3.select('#graph-group').selectAll('.temporary-link').remove();

    // const { x, y } = convertClientToSVG(event);

    // create a new temporary link
    tempLink.value = d3
      .select(`#graph-group`)
      .append('g')
      .attr('class', 'temporary-link')
      .append('line')
      .attr('stroke', '#FFAC1C') // the color of the temporary link
      .attr('stroke-width', 2) // the width of the temporary link
      .attr('stroke-dasharray', '5,5') // dashed style
      .attr('x1', node.x) // starting point x coordinate
      .attr('y1', node.y) // starting point y coordinate
      .attr('x2', node.x) // ending point x coordinate (same as starting point)
      .attr('y2', node.y) // ending point y coordinate (same as starting point)
      .attr('marker-end', 'url(#arrow-selected)'); // ending point y coordinate (same as starting point)
  };

  const stopDrawTempLink = () => {
    d3.select('.graph-content').selectAll('.temporary-link').remove();
    drawingLinkNode.value = null;
  };

  const startAddRelationship = async (event: Event) => {
    event.preventDefault();
    event.stopPropagation();

    hideContextMenu();

    isDrawingLink.value = true;

    if (selectedNodeRef.value) {
      drawingLinkNode.value = selectedNodeRef.value;
      markDrawingLinkNode(drawingLinkNode.value);
      drawTempLink(drawingLinkNode.value);
      selectedNodeRef.value.editable = false;
      selectedNodeRef.value = null;
    }

    const { translateX, translateY } = calculateTransform(
      zoomLevel.value.scale
    );
    zoomLevel.value.translateX = translateX;
    zoomLevel.value.translateY = translateY;
    const graphContent = d3.select('.graph-content svg > g');
    graphContent.attr(
      'transform',
      `translate(${zoomLevel.value.translateX + panOffset.value.x}, 
      ${zoomLevel.value.translateY + panOffset.value.y}) scale(${
        zoomLevel.value.scale
      })`
    );
  };

  const stopAddRelationship = () => {
    isDrawingLink.value = false;
    if (drawingLinkNode.value) {
      unmarkDrawingLinkNode(drawingLinkNode.value);
      drawingLinkNode.value = null;
    }
    stopDrawTempLink();
  };

  const highlightNode = async (element: HTMLElement) => {
    d3.select(element)
      .selectAll('circle')
      .attr('stroke', '#FFAC1C') // highlight selected node
      .attr('stroke-width', 2)
      .attr('box-shadow', '2px 2px 4px rgba(0, 0, 0, 0.2)');
  };

  const unhighlightNode = async (element: HTMLElement) => {
    d3.select(element)
      .selectAll('circle')
      .attr('stroke', '#708090') // Border color
      .attr('stroke-width', 1) // Border thickness
      .attr('box-shadow', 'none');
  };

  const onNodeLeave = async (event: MouseEvent, node: NodeRecord) => {
    if (node.id === selectedNodeRef.value?.id) {
      return;
    }

    if (node.id === drawingLinkNode.value?.id) {
      return;
    }
    if (!event.currentTarget) {
      return;
    }
    unhighlightNode(event.currentTarget as HTMLElement);
  };

  const onNodeEnter = async (event: MouseEvent) => {
    highlightNode(event.currentTarget as HTMLElement);
  };

  const onNodeSelect = async (event: MouseEvent, node: NodeRecord) => {
    // Emit the selected node
    resetStyles();
    if (isDrawingLink.value) {
      if (!drawingLinkNode.value) {
        drawingLinkNode.value = node;
        markDrawingLinkNode(node);
        drawTempLink(node);
      } else {
        if (drawingLinkNode.value.id === node.id) {
          stopAddRelationship();
          return;
        }

        const response = await addGraphRelationship({
          libId: knowledgeLibID.value,
          subjectId: node.subjectId,
          sourceElementId: drawingLinkNode.value.elementId,
          targetElementId: node.elementId,
          type: 'RELATED_TO',
        });
        const { data } = response;

        if (data) {
          graphRecordData.value.links.push(data);
          EventBus.emit('linkAdded', data);

          fecthOverview();
        }
        // Add link
        stopAddRelationship();
      }
    } else {
      selectedNodeRef.value = node;
      if (selectedLinkRef.value) {
        selectedLinkRef.value.editable = false;
      }
      selectedLinkRef.value = null;
      highlightNode(event.currentTarget as HTMLElement);
      knowledgeStore.selectedNode = node;
      knowledgeStore.selectedRelationship = undefined;
      knowledgeStore.overview = undefined;
      EventBus.emit('graphSelected');
    }
  };

  const onNodeRightClick = async (event: MouseEvent, node: NodeRecord) => {
    if (isDrawingLink.value) {
      stopAddRelationship();
    } else {
      onNodeSelect(event, node);
      showContextMenu(event);
    }
  };

  const onLinkSelect = (event: MouseEvent, link: RelationshipRecord) => {
    // set the selected link
    resetStyles();
    if (selectedNodeRef.value) {
      selectedNodeRef.value.editable = false;
    }
    selectedNodeRef.value = null;
    selectedLinkRef.value = link;
    selectedLinkRef.value.editable = false;
    d3.select(event.currentTarget as HTMLElement)
      .selectAll('.link-visible')
      .attr('stroke', '#F4C430') // highlight selected link
      .attr('stroke-width', 2)
      .attr('stroke-opacity', 1)
      .attr('marker-end', 'url(#arrow-selected)');

    knowledgeStore.selectedNode = undefined;
    knowledgeStore.selectedRelationship = selectedLinkRef.value;
    knowledgeStore.overview = undefined;
    EventBus.emit('graphSelected');
  };

  const drag = (simulation: any) => {
    const dragstarted = (event: any, d: any) => {
      if (isDrawingLink.value) {
        return;
      }
      // if (!event.active) {
      //   simulation.alphaTarget(0.3).restart();
      // }
      d.fx = d.x;
      d.fy = d.y;
    };

    const dragged = (event: any, d: any) => {
      if (isDrawingLink.value) {
        return;
      }
      if (simulation.alphaTarget() < 0.3) {
        simulation.alphaTarget(0.3).restart();
      }
      d.fx = event.x;
      d.fy = event.y;

      // Update the node's position in the data model
      const nodeIndex = graphRecordData.value.nodes.findIndex(
        (node) => node.id === d.id
      );
      if (nodeIndex !== -1) {
        graphRecordData.value.nodes[nodeIndex].x = d.fx;
        graphRecordData.value.nodes[nodeIndex].y = d.fy;
      }

      const { translateX, translateY } = calculateTransform(
        zoomLevel.value.scale
      );
      zoomLevel.value.translateX = translateX;
      zoomLevel.value.translateY = translateY;
    };

    const dragended = (event: any, d: any) => {
      if (isDrawingLink.value) {
        return;
      }
      if (!event.active) {
        simulation.alphaTarget(0);
      }
      d.fx = event.x; // Set fixed position to the current x position
      d.fy = event.y; // Set fixed position to the current y position

      // Update the node's position in the data model
      const nodeIndex = graphRecordData.value.nodes.findIndex(
        (node) => node.id === d.id
      );
      if (nodeIndex !== -1) {
        graphRecordData.value.nodes[nodeIndex].x = event.x;
        graphRecordData.value.nodes[nodeIndex].y = event.y;
      }
    };

    return d3
      .drag()
      .on('start', dragstarted)
      .on('drag', dragged)
      .on('end', dragended);
  };

  const clearGraph = () => {
    d3.select('.graph-content').selectAll('svg').remove(); // Clear previous graph elements
    graphRecordData.value.nodes = [];
    graphRecordData.value.links = [];
  };

  const calculateAlphaDecay = (nodes: NodeRecord[]) => {
    if (!nodes || nodes.length === 0) return 1.0;

    if (nodes.length >= 500) {
      return 0.8;
    }
    if (nodes.length >= 300) {
      return 0.7;
    }
    if (nodes.length >= 200) {
      return 0.6;
    }
    if (nodes.length >= 150) {
      return 0.5;
    }
    if (nodes.length >= 100) {
      return 0.4;
    }
    if (nodes.length >= 50) {
      return 0.3;
    }

    return 0.2;
  };

  const drawNodes = (graphGroup: any, simulation: any) => {
    const colorScale = {
      ROOT: '#FA5F55',
      SUBJECT: '#E4D00A',
      INFO: '#9FE2BF',
      PROMPT: '#A7C7E7',
      HUMAN: '#5F9EA0',
      QUESTION: '#FFE5B4',
      DEFAULT: '#EADDCA',
    };

    const sizeScale = {
      ROOT: 16,
      SUBJECT: 15,
      INFO: 14,
      PROMPT: 14,
      HUMAN: 14,
      QUESTION: 14,
      DEFAULT: 14,
    };

    const node = graphGroup
      .selectAll('g.node')
      .data(graphRecordData.value.nodes)
      .enter()
      .append('g')
      .attr('class', 'node')
      .attr('id', (d: NodeRecord) => `node-${d.id}`);

    node
      .append('circle')
      .attr(
        'r',
        (d: NodeRecord) =>
          sizeScale[(d as NodeRecord).type as keyof typeof sizeScale] ||
          sizeScale.DEFAULT
      )
      .attr(
        'fill',
        (d: NodeRecord) =>
          colorScale[(d as NodeRecord).type as keyof typeof colorScale] ||
          colorScale.DEFAULT
      )
      .attr('class', 'node-circle')
      .attr('stroke', '#708090') // Border color
      .attr('stroke-width', 1); // Border thickness

    node
      .append('text')
      .attr('text-anchor', 'middle')
      .attr('dy', 4) // Center text vertically within the node
      .style('pointer-events', 'none') // Disable pointer events for text
      .style('user-select', 'none') // Prevent text selection
      .style('cursor', 'default') // Change cursor to default
      .text((d: NodeRecord) => (d as NodeRecord).id);

    node
      .on('click', (event: MouseEvent, d: NodeRecord) => {
        onNodeSelect(event, d);
      })
      .on('mouseleave', (event: MouseEvent, d: NodeRecord) => {
        onNodeLeave(event, d);
      })
      .on('mouseenter', (event: MouseEvent) => {
        onNodeEnter(event);
      })
      .on('contextmenu', (event: MouseEvent, d: NodeRecord) => {
        onNodeRightClick(event, d);
      })
      .call(drag(simulation));

    return node;
  };

  const onLinkRightClick = (event: MouseEvent, link: RelationshipRecord) => {
    if (isDrawingLink.value) {
      stopAddRelationship();
    } else {
      onLinkSelect(event, link);
      showContextMenu(event);
    }
  };

  const drawLinks = (graphGroup: any) => {
    const link = graphGroup
      .selectAll('g.link')
      .data(graphRecordData.value.links)
      .enter()
      .append('g')
      .attr('class', 'link')
      .attr('id', (d: RelationshipRecord) => `link-${d.id}`);

    link
      .append('line')
      .attr('stroke', 'transparent')
      .attr('stroke-width', 16) // Scale stroke width
      .attr('class', 'link-invisible')
      .attr('marker-start', null)
      .attr('marker-end', null);

    link
      .append('line')
      .attr('stroke', '#999')
      .attr('stroke-opacity', 0.6)
      .attr('class', 'link-visible')
      .attr('stroke-width', 1) // Scale stroke width
      .attr('marker-start', null)
      .attr('marker-end', 'url(#arrow)');

    link
      .append('text')
      .style('pointer-events', 'none') // Disable pointer events for text
      .style('user-select', 'none') // Prevent text selection
      .style('cursor', 'default') // Change cursor to default
      .text((d: RelationshipRecord) => d.type)
      .attr('fill', '#000')
      .attr('font-size', `8px`) // Scale font size
      .attr('text-anchor', 'middle');

    link
      .on('click', (event: MouseEvent, d: RelationshipRecord) => {
        onLinkSelect(event, d);
      })
      .on('contextmenu', (event: MouseEvent, d: RelationshipRecord) => {
        onLinkRightClick(event, d);
      });

    return link;
  };

  const defineArrowMarker = (graphGroup: any) => {
    graphGroup
      .append('defs')
      .append('marker')
      .attr('id', 'arrow')
      .attr('viewBox', '0 0 10 10')
      .attr('refX', 10)
      .attr('refY', 5)
      .attr('markerWidth', 6)
      .attr('markerHeight', 8)
      .attr('orient', 'auto')
      .append('path')
      .attr('d', 'M0,0 L10,5 L0,10 Z')
      .attr('fill', '#999');

    graphGroup
      .append('defs')
      .append('marker')
      .attr('id', 'arrow-selected')
      .attr('viewBox', '0 0 10 10')
      .attr('refX', 10)
      .attr('refY', 5)
      .attr('markerWidth', 3)
      .attr('markerHeight', 4)
      .attr('orient', 'auto')
      .append('path')
      .attr('d', 'M0,0 L10,5 L0,10 Z')
      .attr('fill', '#F4C430');
  };

  const tickGraph = (simulation: any, node: any, link: any) => {
    simulation.nodes(graphRecordData.value.nodes).on('tick', () => {
      node.attr('transform', (d: NodeRecord) => `translate(${d.x},${d.y})`);

      link
        .selectAll('line')
        .attr('x1', (d: any) => {
          const dx = d.target.x - d.source.x; // the x distance between the two nodes
          const dy = d.target.y - d.source.y; // the y distance between the two nodes
          const distance = Math.max(30, Math.sqrt(dx * dx + dy * dy)); // the distance between the two nodes
          const radius = d.source.radius || 14;

          return d.source.x + (dx / distance) * radius; // ajust the starting point
        })
        .attr('y1', (d: any) => {
          const dx = d.target.x - d.source.x;
          const dy = d.target.y - d.source.y;
          const distance = Math.max(30, Math.sqrt(dx * dx + dy * dy));
          const radius = d.source.radius || 14;
          return d.source.y + (dy / distance) * radius; // ajust the starting point
        })
        .attr('x2', (d: any) => {
          const dx = d.source.x - d.target.x;
          const dy = d.source.y - d.target.y;
          const distance = Math.max(30, Math.sqrt(dx * dx + dy * dy));
          const radius = d.target.radius || 14;
          return d.target.x + (dx / distance) * radius; // ajust the endpoint
        })
        .attr('y2', (d: any) => {
          const dx = d.source.x - d.target.x;
          const dy = d.source.y - d.target.y;
          const distance = Math.max(30, Math.sqrt(dx * dx + dy * dy));
          const radius = d.target.radius || 14;
          return d.target.y + (dy / distance) * radius; // ajust the endpoint
        });

      link.selectAll('text').attr('transform', (d: any) => {
        const dx = (d.target?.x || 0) - (d.source?.x || 0);
        const dy = (d.target?.y || 0) - (d.source?.y || 0);
        let angle = Math.atan2(dy, dx) * (180 / Math.PI); // Compute angle in degrees

        // Determine if the target is to the left of the source
        const isTargetToLeft = dx < 0;

        // Adjust the angle for horizontal links when target is on the left
        if (isTargetToLeft && Math.abs(dy) < 90) {
          angle += 180; // Flip the text by adding 180 degrees
        }

        const x = ((d.source?.x || 0) + (d.target?.x || 0)) / 2; // Midpoint x
        const y = ((d.source?.y || 0) + (d.target?.y || 0)) / 2; // Midpoint y
        return `translate(${x}, ${y}) rotate(${angle}, 0, 0)`; // Rotate around the element's origin
      });
    });
  };

  const drawGraph = () => {
    d3.select('.graph-content').selectAll('svg').remove(); // Clear previous graph elements
    const width = graphContentRef.value?.clientWidth || 800;
    const height = graphContentRef.value?.clientHeight || 400;
    const svg = d3
      .select('.graph-content')
      .append('svg')
      .attr('width', width)
      .attr('height', height);
    // Add a rectangle for the border
    svg
      .append('rect')
      .attr('x', 0)
      .attr('y', 0)
      .attr('width', width)
      .attr('height', height)
      .attr('fill', 'none')
      .attr('stroke', '#D3D3D3')
      .attr('stroke-width', 2);

    const graphGroup = svg.append('g').attr('id', 'graph-group'); // Add a group for graph elements

    // Define arrow markers
    defineArrowMarker(graphGroup);

    const simulation = d3
      .forceSimulation(graphRecordData.value.nodes)
      .force(
        'link',
        d3
          .forceLink()
          .id((node: d3.SimulationNodeDatum) => {
            const d = node as NodeRecord;
            return d.id;
          })
          .distance(100)
      )
      .force('charge', d3.forceManyBody().strength(-100))
      .force('center', d3.forceCenter(width / 2, height / 2))
      .alphaDecay(calculateAlphaDecay(graphRecordData.value.nodes));

    const link = drawLinks(graphGroup);
    const node = drawNodes(graphGroup, simulation);
    tickGraph(simulation, node, link);

    // simulation.force('link').links(graphRecordData.value.links);
    const linkForce = simulation.force('link') as d3.ForceLink<
      NodeRecord,
      RelationshipRecord
    >;
    linkForce.links(graphRecordData.value?.links);

    simulation.on('end', () => {
      if (graphRecordData.value.nodes.length > 0) {
        if (zoomLevel.value.scale === 0.0) {
          zoomLevel.value = calculateViewDimensions();
        }
        if (isFitingView.value || graphGroup.attr('transform') === null) {
          graphGroup.attr(
            'transform',
            `translate(${zoomLevel.value.translateX}, ${zoomLevel.value.translateY}) scale(${zoomLevel.value.scale})`
          );
        }
      }
      isFitingView.value = false;
    });
  };

  const zoomIn = () => {
    zoomLevel.value.scale = Math.min(6.0, zoomLevel.value.scale * 1.25);
    const { translateX, translateY } = calculateTransform(
      zoomLevel.value.scale
    );
    zoomLevel.value.translateX = translateX;
    zoomLevel.value.translateY = translateY;
    // Apply transform to the graph
    const graphContent = d3.select('.graph-content svg > g');

    graphContent.attr(
      'transform',
      `translate(${zoomLevel.value.translateX + panOffset.value.x}, 
      ${zoomLevel.value.translateY + panOffset.value.y}) scale(${
        zoomLevel.value.scale
      })`
    );
  };

  const zoomOut = () => {
    zoomLevel.value.scale = Math.max(0.16, zoomLevel.value.scale * 0.8);
    const { translateX, translateY } = calculateTransform(
      zoomLevel.value.scale
    );
    zoomLevel.value.translateX = translateX;
    zoomLevel.value.translateY = translateY;
    // Apply transform to the graph
    const graphContent = d3.select('.graph-content svg > g');

    graphContent.attr(
      'transform',
      `translate(${zoomLevel.value.translateX + panOffset.value.x}, 
      ${zoomLevel.value.translateY + panOffset.value.y}) scale(${
        zoomLevel.value.scale
      })`
    );
  };

  const resetView = () => {
    zoomLevel.value.scale = 1.0;
    const { translateX, translateY } = calculateTransform(
      zoomLevel.value.scale
    );
    zoomLevel.value.translateX = translateX;
    zoomLevel.value.translateY = translateY;
    const graphContent = d3.select('.graph-content svg > g');
    graphContent.attr(
      'transform',
      `translate(${zoomLevel.value.translateX + panOffset.value.x}, 
      ${zoomLevel.value.translateY + panOffset.value.y}) scale(${
        zoomLevel.value.scale
      })`
    );
  };

  const fitView = () => {
    isFitingView.value = true;
    const { scale, translateX, translateY } = calculateViewDimensions();
    zoomLevel.value = { scale, translateX, translateY };
    panOffset.value = { x: 0, y: 0 };
    const graphContent = d3.select('.graph-content svg > g');
    graphContent.attr(
      'transform',
      `translate(${zoomLevel.value.translateX + panOffset.value.x}, 
      ${zoomLevel.value.translateY + panOffset.value.y}) scale(${
        zoomLevel.value.scale
      })`
    );
  };

  const exportToSVG = () => {
    const graphElement = graphContentRef.value?.querySelector('svg');

    if (!graphElement) {
      Message.error(t('knowledge.graph.notFoundSVG'));
      return;
    }

    // convert SVG element to string
    const svgData = new XMLSerializer().serializeToString(graphElement);

    // create Blob object
    const blob = new Blob([svgData], { type: 'image/svg+xml;charset=utf-8' });

    // create download link
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = 'network-graph.svg';
    link.click();

    // release URL object
    URL.revokeObjectURL(link.href);
  };

  const exportToPNG = () => {
    const graphElement = graphContentRef.value; // Vue ref
    html2canvas(graphElement as HTMLElement).then((canvas) => {
      const link = document.createElement('a');
      link.download = 'network-graph.png';
      link.href = canvas.toDataURL('image/png');
      link.click();
    });
  };

  /* eslint-disable new-cap */
  const exportToPDF = async () => {
    const graphElement = graphContentRef.value?.querySelector('svg');

    if (!graphElement) {
      Message.error(t('knowledge.graph.notFoundSVG'));
      return;
    }

    // create a new jsPDF instance
    const pdf = new jsPDF({
      orientation: 'landscape',
      unit: 'pt',
      format: [graphElement.clientWidth, graphElement.clientHeight],
    });

    // clone the SVG element
    const svgElement = graphElement.cloneNode(true) as SVGElement; // deep clone

    // remove the viewBox attribute
    await svg2pdf(svgElement as SVGElement, pdf, {
      x: 0,
      y: 0,
      width: graphElement.clientWidth,
      height: graphElement.clientHeight,
    });

    // save the PDF
    pdf.save('network-graph.pdf');
  };
  /* eslint-enable new-cap */

  const { loading, setLoading } = useLoading(false);
  const fetchData = async () => {
    try {
      // Fetch data
      if (!subjectIDs.value || subjectIDs.value.length === 0) {
        clearGraph();
      } else {
        setLoading(true);
        const response = await queryGraph(knowledgeLibID.value, {
          subjectIds: subjectIDs.value,
          type:
            queryCondition.value.selectedNodeType &&
            queryCondition.value.selectedNodeType !== 'ALL'
              ? queryCondition.value.selectedNodeType
              : null,
          content: queryCondition.value.searchKeyword,
        });
        const { data } = response;
        graphRecordData.value = data;
        selectedLinkRef.value = null;
        selectedNodeRef.value = null;
        knowledgeStore.selectedNode = undefined;
        knowledgeStore.selectedRelationship = undefined;
        knowledgeStore.overview = data.overview;
        EventBus.emit('graphSelected');
        setLoading(false);
        if (graphRecordData.value.nodes.length > 0) {
          drawGraph();
        } else {
          clearGraph();
        }

        if (data.status.trim() === 'GENERATING') {
          setTimeout(fetchData, 10000);
        } else {
          EventBus.emit('finishGenratingGraph');
        }
      }
    } catch (err) {
      // Removed console statement
    } finally {
      setLoading(false);
    }
  };

  const refreshGraph = async () => {
    zoomLevel.value = { scale: 0.0, translateX: 0, translateY: 0 };
    fetchData();
  };

  const handleMouseMoveForLink = (event: MouseEvent) => {
    if (tempLink.value) {
      const { x, y } = convertClientToSVG(event);
      tempLink.value.attr('x2', x - 1).attr('y2', y - 1);
    }
  };

  const isZoomInDisabled = computed(() => zoomLevel.value.scale >= 6.0);
  const isZoomOutDisabled = computed(() => zoomLevel.value.scale <= 0.16);

  const initializeGraphDragging = () => {
    const graphContent = graphContentRef.value as HTMLElement | null;
    if (!graphContent) {
      return;
    }

    let isDragging = false;
    let previousMousePosition = { x: 0, y: 0 };
    graphContent.addEventListener('mouseleave', () => {
      isDragging = false;
      previousMousePosition = { x: 0, y: 0 };
      graphContent.style.cursor = 'default';
    });
    graphContent.addEventListener('mousedown', (event) => {
      isDragging = true;
      previousMousePosition = { x: event.clientX, y: event.clientY };
      graphContent.style.cursor = 'grabbing';
    });
    graphContent.addEventListener('contextmenu', (event) => {
      if (isDrawingLink.value) {
        const target = event.target as HTMLElement;
        const isNode = target.classList.contains('node-circle');
        if (!isNode) {
          stopAddRelationship();
          isDragging = false;
          graphContent.style.cursor = 'default';
        }
      }

      event.preventDefault();
      event.stopPropagation();
    });
    graphContent.addEventListener('mouseup', () => {
      hideContextMenu();
      if (isDragging) {
        isDragging = false;
        // previousMousePosition = { x: 0, y: 0 };
        graphContent.style.cursor = 'default';
        // Reset selected node
        resetStyles();
        if (selectedNodeRef.value) {
          selectedNodeRef.value.editable = false;
        }
        if (selectedLinkRef.value) {
          selectedLinkRef.value.editable = false;
        }
        selectedNodeRef.value = null;
        selectedLinkRef.value = null;
        knowledgeStore.selectedNode = undefined;
        knowledgeStore.selectedRelationship = undefined;
        knowledgeStore.overview = graphRecordData.value.overview;
        EventBus.emit('graphSelected');
      }
    });

    graphContent.addEventListener('mousemove', (event) => {
      if (isDragging) {
        previousMousePosition = panGraph(event, previousMousePosition);
        handleMouseMoveForLink(event);
      } else {
        handleMouseMoveForLink(event);
        graphContent.style.cursor = 'default';
      }
    });
  };

  const addNode = async (event: Event) => {
    event.preventDefault();
    event.stopPropagation();

    hideContextMenu();

    if (subjectIDs.value?.length === 0) {
      Message.warning(t('knowledge.graph.noSubjectSelected'));
      return;
    }

    try {
      // invoke api
      const newNode = {
        parentElementId: selectedNodeRef.value?.elementId,
        libId: knowledgeLibID.value,
        subjectId: subjectIDs.value?.[0],
        content: '',
      };
      const response = await addGraphNode(newNode);
      const { data } = response;

      if (data) {
        if (data.node) {
          // put new node into graph
          data.node.x = Math.random() * 800; // random x
          data.node.y = Math.random() * 600;
          graphRecordData.value.nodes.push(data.node);
        }

        if (data.relationship) {
          graphRecordData.value.links.push(data.relationship);
        }

        drawGraph();

        fecthOverview();
      }
    } catch (error) {
      Message.error(t('knowledge.graph.addNodeFailed'));
    }
  };

  const deleteNode = async (event: Event) => {
    event.preventDefault();
    event.stopPropagation();

    if (subjectIDs.value?.length === 0) {
      Message.warning(t('knowledge.graph.noSubjectSelected'));
      return;
    }

    const node = selectedNodeRef.value;
    if (!node) {
      Message.warning(t('knowledge.graph.noNodeSelected'));
      return;
    }

    const { elementId } = node;
    const response = await deleteGraphNode(elementId);
    const { data } = response;

    if (data && data.success) {
      graphRecordData.value.nodes = graphRecordData.value.nodes.filter(
        (n) => n.elementId !== elementId
      );
      // remove svg element
      d3.select('.graph-content').selectAll(`#node-${node.id}`).remove();
      if (selectedNodeRef.value) {
        selectedNodeRef.value.editable = false;
      }
      selectedNodeRef.value = null;
      knowledgeStore.selectedNode = undefined;
      knowledgeStore.selectedRelationship = undefined;
      EventBus.emit('graphSelected');
      fecthOverview();
    }
  };

  const deleteRelationship = async (event: Event) => {
    event.preventDefault();
    event.stopPropagation();

    const relationship = selectedLinkRef.value;
    if (!relationship) {
      Message.warning(t('knowledge.graph.noRelationshipSelected'));
      return;
    }

    const { elementId } = relationship;
    const response = await deleteGraphRelationship(elementId);
    const { data } = response;

    if (data && data.success) {
      graphRecordData.value.links = graphRecordData.value.links.filter(
        (r) => r.elementId !== elementId
      );
      d3.select(`#link-${relationship.id}`).remove();
      if (selectedLinkRef.value) {
        selectedLinkRef.value.editable = false;
      }
      selectedLinkRef.value = null;
      knowledgeStore.selectedNode = undefined;
      knowledgeStore.selectedRelationship = undefined;
      EventBus.emit('graphSelected');
      fecthOverview();
    }
  };

  const updateNode = async (node: NodeRecord) => {
    const response = await updateNodeInfo(
      node,
      knowledgeStore.currentEmbedding ? knowledgeStore.currentEmbedding : null,
      knowledgeStore.maxTokensEachChunk
    );
    const { data } = response;
    if (data) {
      graphRecordData.value.nodes = graphRecordData.value.nodes.map((n) => {
        if (n.elementId === node.elementId) {
          n.content = data.content;
          n.contentVector = data.contentVector;
        }
        return n;
      });
    }
  };

  const updateLink = async (link: RelationshipRecord) => {
    const response = await updateRelationshipInfo(
      link,
      knowledgeStore.currentEmbedding ? knowledgeStore.currentEmbedding : null,
      knowledgeStore.maxTokensEachChunk
    );
    const { data } = response;
    if (data) {
      graphRecordData.value.links = graphRecordData.value.links.map((r) => {
        if (r.elementId === link.elementId) {
          r.content = data.content;
          r.contentVector = data.contentVector;
        }
        return r;
      });
    }
  };

  const editObject = async (event: Event) => {
    event.preventDefault();
    event.stopPropagation();
    if (selectedNodeRef.value) {
      selectedNodeRef.value.editable = true;
      knowledgeStore.selectedNode = selectedNodeRef.value;
      knowledgeStore.selectedRelationship = undefined;
      knowledgeStore.overview = undefined;
      EventBus.emit('graphSelected');
    } else if (selectedLinkRef.value) {
      selectedLinkRef.value.editable = true;
      knowledgeStore.selectedNode = undefined;
      knowledgeStore.selectedRelationship = selectedLinkRef.value;
      knowledgeStore.overview = undefined;
      EventBus.emit('graphSelected');
    } else {
      Message.warning(t('knowledge.graph.noObjectSelected'));
    }
    hideContextMenu();
  };

  const deleteObject = async (event: Event) => {
    event.preventDefault();
    event.stopPropagation();

    if (selectedNodeRef.value) {
      deleteNode(event);
    } else if (selectedLinkRef.value) {
      deleteRelationship(event);
    } else {
      Message.warning(t('knowledge.graph.noObjectSelected'));
    }
    hideContextMenu();
  };

  onMounted(() => {
    EventBus.off('knowledgeSubjectSelecteChange');
    EventBus.on('knowledgeSubjectSelecteChange', (evntData: any) => {
      // Reset variables
      knowledgeLibID.value = evntData.libId;
      subjectIDs.value = evntData.subjectIDs;

      fetchData();
    });

    EventBus.off('refresh_graph');
    EventBus.on('refresh_graph', () => {
      refreshGraph();
    });

    EventBus.off('linkAdded');
    EventBus.on('linkAdded', () => {
      drawGraph();
    });

    EventBus.off('update_node');
    EventBus.on('update_node', (node: any) => {
      updateNode(node);
    });

    EventBus.off('update_link');
    EventBus.on('update_link', (link: any) => {
      updateLink(link);
    });

    EventBus.off('ganerate_graph_answer');
    EventBus.on('ganerate_graph_answer', (data: any) => {
      if (data && graphRecordData.value) {
        graphRecordData.value.nodes.push(data.node);
        graphRecordData.value.links.push(data.relationship);
        drawGraph();
        fecthOverview();
      }
    });

    EventBus.off('ganerate_graph_questions');
    EventBus.on('ganerate_graph_questions', (data: any) => {
      if (data && graphRecordData.value) {
        if (data.nodes) {
          forEach(data.nodes, (item) => {
            graphRecordData.value.nodes.push(item);
          });
        }

        if (data.relationships) {
          forEach(data.relationships, (item) => {
            graphRecordData.value.links.push(item);
          });
        }

        drawGraph();
        fecthOverview();
      }
    });

    window.addEventListener('resize', drawGraph);

    initializeGraphDragging();
  });
</script>

<style scoped lang="less">
  .graph {
    &-wrapper {
      position: relative;
    }
    &-content {
      display: block;
      margin: 0 auto;
      width: 100%;
      height: 400px;
      position: relative;
    }

    &-mode-bar {
      display: flex;
      justify-content: space-between;
      margin-top: 16px;
      position: relative;
    }
    &-zoom-bar-container {
      position: absolute;
      display: flex;
      flex-direction: column;
      top: 0;
      left: 0;
    }
    &-zoom-bar {
      position: relative;
      display: flex;
      flex-direction: column;
      top: 0;
      left: 0;
      border: 1px solid #ccc;
      box-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1);
      border-radius: 4px;
      background-color: #fff;
    }
    &-operation-bar {
      position: absolute;
      top: 0;
      right: 0;
      display: flex;
      border: 1px solid #ccc;
      box-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1);
      border-radius: 4px;
      background-color: #fff;
    }
  }

  .menu-graph {
    width: 100%;
    box-sizing: border-box;
    background-color: var(--color-neutral-2);
  }

  .menu-graph .arco-menu {
    box-shadow: 0 0 1px rgba(0, 0, 0, 0.3);
  }

  #context-menu {
    position: absolute;
    background-color: #fff;
    border: 1px solid #ccc;
    box-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1);
    border-radius: 4px;
    padding: 8px 0;
    z-index: 1000;
    ul {
      list-style: none;
      padding: 0;
      margin: 0;
      li {
        padding: 8px 16px;
        cursor: pointer;
        &:hover {
          background-color: #f0f0f0;
        }
      }
    }
  }
</style>
