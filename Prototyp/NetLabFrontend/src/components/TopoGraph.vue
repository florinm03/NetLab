<template>
    <div class="topology-container">
      <div class="topology-header">
        <h2>DHCP Configuration</h2>
        <div class="topology-controls">
          <button class="control-button" @click="resetNodes">Reset</button>
          <button class="control-button" @click="toggleSimulation">{{ isSimulating ? 'Stop' : 'Simulate' }}</button>
        </div>
      </div>
      
      <div class="vue-flow-wrapper">
        <VueFlow
          v-model="elements"
          :defaultZoom="1.5"
          @nodeClick="onNodeClick"
          @connect="onConnect"
          class="vue-flow-canvas"
        >
          <template #node-router="nodeProps">
            <RouterNode v-bind="nodeProps" />
          </template>
          <template #node-switch="nodeProps">
            <SwitchNode v-bind="nodeProps" />
          </template>
          <template #node-client="nodeProps">
            <ClientNode v-bind="nodeProps" />
          </template>
          <template #node-dhcp="nodeProps">
            <DHCPNode v-bind="nodeProps" />
          </template>
          
          <Background pattern-color="#aaa" gap="8" />
          <MiniMap />
          <Controls />
          
          <Panel position="top-right">
            <div class="simulation-panel" v-if="isSimulating">
              <div class="simulation-status">
                <span class="status-dot active"></span>
                Simulation Active
              </div>
              <div class="message-log">
                <p v-for="(msg, idx) in simulationMessages" :key="idx" :class="msg.type">
                  {{ msg.text }}
                </p>
              </div>
            </div>
          </Panel>
        </VueFlow>
      </div>
      
      <div class="topology-info">
        <div class="selected-node-info" v-if="selectedNode">
          <h3>{{ selectedNode.data.label }}</h3>
          <div class="node-properties">
            <div class="property" v-for="(value, key) in selectedNode.data.properties" :key="key">
              <span class="property-label">{{ key }}:</span>
              <span class="property-value">{{ value }}</span>
            </div>
          </div>
        </div>
        <div class="topology-description" v-else>
          <h3>DHCP Configuration Scenario</h3>
          <p>This topology demonstrates how DHCP assigns IP addresses dynamically in a network. Clients request an IP address from the DHCP server through the router and switch.</p>
          <p>Click on any node to view its properties. Drag nodes to rearrange the network.</p>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  import { ref, computed, onMounted } from 'vue';
  import { VueFlow, Background, MiniMap, Controls, Panel, useVueFlow } from '@vue-flow/core';
  import { v4 as uuidv4 } from 'uuid';
  import '@vue-flow/core/dist/style.css';
  import '@vue-flow/core/dist/theme-default.css';
  
  // Import custom node components
  import RouterNode from './RouterNode.vue';
//   import SwitchNode from './nodes/SwitchNode.vue';
//   import ClientNode from './nodes/ClientNode.vue';
//   import DHCPNode from './nodes/DHCPNode.vue';
  
  export default {
    name: 'DHCPTopology',
    components: {
      VueFlow,
      Background,
      MiniMap,
      Controls,
      Panel,
      RouterNode,
      SwitchNode,
      ClientNode,
      DHCPNode
    },
    
    setup() {
      const selectedNode = ref(null);
      const isSimulating = ref(false);
      const simulationMessages = ref([]);
      const simulationInterval = ref(null);
      
      // Define initial nodes
      const initialNodes = [
        {
          id: '1',
          type: 'router',
          position: { x: 250, y: 50 },
          data: { 
            label: 'Router',
            properties: {
              'IP Address': '192.168.1.1',
              'Subnet Mask': '255.255.255.0',
              'MAC Address': '00:1A:2B:3C:4D:5E',
              'Status': 'Online'
            }
          }
        },
        {
          id: '2',
          type: 'switch',
          position: { x: 250, y: 200 },
          data: { 
            label: 'Switch',
            properties: {
              'MAC Address': '00:5F:6E:7D:8C:9B',
              'Status': 'Online',
              'Ports': '24',
              'Active Connections': '3'
            }
          }
        },
        {
          id: '3',
          type: 'client',
          position: { x: 100, y: 350 },
          data: { 
            label: 'Client',
            properties: {
              'Hostname': 'PC-01',
              'MAC Address': '00:9A:8B:7C:6D:5E',
              'IP Address': 'Requesting...',
              'Status': 'Booting'
            }
          }
        },
        {
          id: '4',
          type: 'dhcp',
          position: { x: 400, y: 350 },
          data: { 
            label: 'DHCP Server',
            properties: {
              'IP Address': '192.168.1.2',
              'Subnet Mask': '255.255.255.0',
              'MAC Address': '00:2C:3D:4E:5F:6A',
              'Status': 'Online',
              'Available IPs': '192.168.1.100 - 192.168.1.200'
            }
          }
        }
      ];
      
      // Define initial edges
      const initialEdges = [
        {
          id: 'e1-2',
          source: '1', // Router
          target: '2', // Switch
          animated: false,
          style: { stroke: '#94a3b8', strokeWidth: 2 }
        },
        {
          id: 'e2-3',
          source: '2', // Switch
          target: '3', // Client
          animated: false,
          style: { stroke: '#94a3b8', strokeWidth: 2 }
        },
        {
          id: 'e2-4',
          source: '2', // Switch
          target: '4', // DHCP
          animated: false,
          style: { stroke: '#94a3b8', strokeWidth: 2 }
        }
      ];
      
      const elements = ref({
        nodes: initialNodes,
        edges: initialEdges
      });
      
      // Node click handler
      const onNodeClick = (_, node) => {
        selectedNode.value = node;
      };
      
      // Connect handler for when users draw new connections
      const onConnect = (params) => {
        const newEdge = {
          id: `e${params.source}-${params.target}`,
          source: params.source,
          target: params.target,
          animated: false,
          style: { stroke: '#94a3b8', strokeWidth: 2 }
        };
        
        elements.value.edges = [...elements.value.edges, newEdge];
      };
      
      // Reset nodes to initial positions
      const resetNodes = () => {
        elements.value.nodes = initialNodes;
        elements.value.edges = initialEdges;
        selectedNode.value = null;
      };
      
      // Toggle simulation
      const toggleSimulation = () => {
        isSimulating.value = !isSimulating.value;
        
        if (isSimulating.value) {
          startSimulation();
        } else {
          stopSimulation();
        }
      };
      
      // Start DHCP simulation
      const startSimulation = () => {
        // Clear messages
        simulationMessages.value = [];
        
        // Reset client status
        const clientNode = elements.value.nodes.find(node => node.id === '3');
        if (clientNode) {
          clientNode.data = {
            ...clientNode.data,
            properties: {
              ...clientNode.data.properties,
              'IP Address': 'Requesting...',
              'Status': 'Booting'
            }
          };
        }
        
        // Animate connections during DHCP process
        const edgeClientToSwitch = elements.value.edges.find(edge => edge.id === 'e2-3');
        const edgeSwitchToDHCP = elements.value.edges.find(edge => edge.id === 'e2-4');
        
        if (edgeClientToSwitch && edgeSwitchToDHCP) {
          // Step 1: DHCP Discovery
          setTimeout(() => {
            edgeClientToSwitch.animated = true;
            edgeClientToSwitch.style = { stroke: '#3b82f6', strokeWidth: 2 };
            simulationMessages.value.push({ 
              type: 'info',
              text: 'Client broadcasts DHCP DISCOVER message' 
            });
          }, 1000);
  
          // Step 2: DHCP Offer
          setTimeout(() => {
            edgeSwitchToDHCP.animated = true;
            edgeSwitchToDHCP.style = { stroke: '#f97316', strokeWidth: 2 };
            simulationMessages.value.push({ 
              type: 'success',
              text: 'DHCP server responds with DHCP OFFER (IP: 192.168.1.100)' 
            });
          }, 3000);
  
          // Step 3: DHCP Request
          setTimeout(() => {
            edgeClientToSwitch.style = { stroke: '#a855f7', strokeWidth: 2 };
            simulationMessages.value.push({ 
              type: 'info',
              text: 'Client sends DHCP REQUEST accepting the offered IP' 
            });
          }, 5000);
  
          // Step 4: DHCP Acknowledge
          setTimeout(() => {
            edgeSwitchToDHCP.style = { stroke: '#22c55e', strokeWidth: 2 };
            simulationMessages.value.push({ 
              type: 'success',
              text: 'DHCP server sends DHCP ACK confirming IP assignment' 
            });
            
            // Update client properties
            if (clientNode) {
              clientNode.data = {
                ...clientNode.data,
                properties: {
                  ...clientNode.data.properties,
                  'IP Address': '192.168.1.100',
                  'Subnet Mask': '255.255.255.0',
                  'Status': 'Connected'
                }
              };
            }
          }, 7000);
  
          // Reset animations after simulation
          setTimeout(() => {
            edgeClientToSwitch.animated = false;
            edgeSwitchToDHCP.animated = false;
            edgeClientToSwitch.style = { stroke: '#94a3b8', strokeWidth: 2 };
            edgeSwitchToDHCP.style = { stroke: '#94a3b8', strokeWidth: 2 };
            
            simulationMessages.value.push({ 
              type: 'info',
              text: 'DHCP configuration complete. Client is now online.' 
            });
            
            isSimulating.value = false;
          }, 9000);
        }
      };
      
      // Stop simulation
      const stopSimulation = () => {
        if (simulationInterval.value) {
          clearInterval(simulationInterval.value);
          simulationInterval.value = null;
        }
        
        // Reset edge animations
        elements.value.edges.forEach(edge => {
          edge.animated = false;
          edge.style = { stroke: '#94a3b8', strokeWidth: 2 };
        });
        
        simulationMessages.value = [];
      };
      
      return {
        elements,
        selectedNode,
        isSimulating,
        simulationMessages,
        onNodeClick,
        onConnect,
        resetNodes,
        toggleSimulation
      };
    }
  };
  </script>
  
  <style scoped>
  .topology-container {
    display: flex;
    flex-direction: column;
    height: 100%;
    font-family: 'Inter', sans-serif;
  }
  
  .topology-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem;
    background-color: #f8fafc;
    border-bottom: 1px solid #e2e8f0;
  }
  
  .topology-header h2 {
    margin: 0;
    color: #0f172a;
    font-size: 1.5rem;
  }
  
  .topology-controls {
    display: flex;
    gap: 0.5rem;
  }
  
  .control-button {
    padding: 0.5rem 1rem;
    background-color: #3b82f6;
    color: white;
    border: none;
    border-radius: 0.25rem;
    cursor: pointer;
    font-size: 0.875rem;
    transition: background-color 0.2s;
  }
  
  .control-button:hover {
    background-color: #2563eb;
  }
  
  .vue-flow-wrapper {
    flex-grow: 1;
    height: 500px;
    position: relative;
  }
  
  .vue-flow-canvas {
    background-color: #f8fafc;
  }
  
  .topology-info {
    padding: 1rem;
    background-color: white;
    border-top: 1px solid #e2e8f0;
  }
  
  .selected-node-info h3,
  .topology-description h3 {
    margin-top: 0;
    color: #0f172a;
  }
  
  .node-properties {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 0.5rem;
  }
  
  .property {
    padding: 0.5rem;
    background-color: #f1f5f9;
    border-radius: 0.25rem;
  }
  
  .property-label {
    font-weight: 500;
    color: #64748b;
  }
  
  .property-value {
    margin-left: 0.5rem;
    color: #0f172a;
  }
  
  .simulation-panel {
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 0.5rem;
    padding: 1rem;
    width: 300px;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  }
  
  .simulation-status {
    display: flex;
    align-items: center;
    margin-bottom: 0.5rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid #e2e8f0;
    font-weight: 500;
  }
  
  .status-dot {
    width: 10px;
    height: 10px;
    border-radius: 50%;
    margin-right: 0.5rem;
  }
  
  .status-dot.active {
    background-color: #22c55e;
    box-shadow: 0 0 0 2px rgba(34, 197, 94, 0.2);
  }
  
  .message-log {
    max-height: 200px;
    overflow-y: auto;
  }
  
  .message-log p {
    margin: 0.25rem 0;
    padding: 0.25rem 0.5rem;
    border-radius: 0.25rem;
    font-size: 0.875rem;
  }
  
  .message-log p.info {
    background-color: #eff6ff;
    color: #1e40af;
  }
  
  .message-log p.success {
    background-color: #f0fdf4;
    color: #166534;
  }
  
  .message-log p.warning {
    background-color: #fffbeb;
    color: #92400e;
  }
  
  .message-log p.error {
    background-color: #fef2f2;
    color: #b91c1c;
  }
  </style>