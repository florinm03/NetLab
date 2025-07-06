<template>
    <div class="router-node" :class="{ selected: selected }">
      <div class="node-header">
        <div class="node-icon">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24">
            <path fill="none" d="M0 0h24v24H0z"/>
            <path d="M11 14v-3h2v3h5a1 1 0 0 1 1 1v6a1 1 0 0 1-1 1H6a1 1 0 0 1-1-1v-6a1 1 0 0 1 1-1h5zm1 7a1 1 0 1 0 0-2 1 1 0 0 0 0 2zm0-3a1 1 0 1 0 0-2 1 1 0 0 0 0 2zm0-3a1 1 0 1 0 0-2 1 1 0 0 0 0 2zm-3 3a1 1 0 1 0 0-2 1 1 0 0 0 0 2zm0 3a1 1 0 1 0 0-2 1 1 0 0 0 0 2zm6-3a1 1 0 1 0 0-2 1 1 0 0 0 0 2zm0 3a1 1 0 1 0 0-2 1 1 0 0 0 0 2zm4-12H5V5h3V2h8v3h3v4z" fill="currentColor"/>
          </svg>
        </div>
        <div class="node-title">{{ data.label }}</div>
      </div>
      <div class="node-content">
        <div class="node-status" :class="getStatusClass(data.properties.Status)">
          {{ data.properties.Status }}
        </div>
        <div class="node-ip">
          <span class="property-label">IP:</span> {{ data.properties['IP Address'] }}
        </div>
      </div>
      <div class="node-ports">
        <div class="port-group">
          <div class="port wan" title="WAN Port"></div>
          <div class="port lan" title="LAN Port 1"></div>
          <div class="port lan" title="LAN Port 2"></div>
          <div class="port lan" title="LAN Port 3"></div>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  export default {
    name: 'RouterNode',
    props: {
      id: {
        type: String,
        required: true
      },
      data: {
        type: Object,
        required: true
      },
      selected: {
        type: Boolean,
        default: false
      }
    },
    methods: {
      getStatusClass(status) {
        if (status === 'Online') return 'status-online';
        if (status === 'Offline') return 'status-offline';
        if (status === 'Warning') return 'status-warning';
        return '';
      }
    }
  };
  </script>
  
  <style scoped>
  .router-node {
    width: 180px;
    background-color: white;
    border: 2px solid #16a34a;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    transition: all 0.2s;
    overflow: hidden;
  }
  
  .router-node.selected {
    box-shadow: 0 0 0 2px rgba(22, 163, 74, 0.5), 0 2px 8px rgba(0, 0, 0, 0.15);
  }
  
  .node-header {
    display: flex;
    align-items: center;
    padding: 8px;
    background-color: #22c55e;
    color: white;
  }
  
  .node-icon {
    margin-right: 8px;
    width: 24px;
    height: 24px;
  }
  
  .node-title {
    font-weight: bold;
    font-size: 14px;
  }
  
  .node-content {
    padding: 8px;
    background-color: #f0fdf4;
  }
  
  .node-status {
    display: inline-block;
    padding: 2px 6px;
    border-radius: 4px;
    font-size: 12px;
    font-weight: 500;
    margin-bottom: 4px;
  }
  
  .status-online {
    background-color: #dcfce7;
    color: #16a34a;
  }
  
  .status-offline {
    background-color: #fee2e2;
    color: #dc2626;
  }
  
  .status-warning {
    background-color: #fef3c7;
    color: #d97706;
  }
  
  .node-ip {
    font-size: 12px;
    color: #334155;
  }
  
  .property-label {
    font-weight: 500;
    color: #64748b;
  }
  
  .node-ports {
    padding: 6px;
    background-color: #e2e8f0;
    display: flex;
    justify-content: center;
  }
  
  .port-group {
    display: flex;
    gap: 6px;
  }
  
  .port {
    width: 16px;
    height: 16px;
    border-radius: 2px;
  }
  
  .port.wan {
    background-color: #3b82f6;
    border: 1px solid #2563eb;
  }
  
  .port.lan {
    background-color: #10b981;
    border: 1px solid #059669;
  }
  </style>