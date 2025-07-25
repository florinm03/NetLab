<template>
    <div class="saved-pcaps">
        <div class="header-section">
            <h2>Gespeicherte PCAP-Dateien</h2>
            <p>Ihre in der Datenbank gespeicherten Netzwerk-Aufzeichnungen</p>
        </div>

        <div v-if="loading" class="loading-section">
            <div class="loading-spinner"></div>
            <p>Lade gespeicherte PCAP-Dateien...</p>
        </div>

        <div v-else-if="pcaps.length === 0" class="empty-state">
            <i class="pi pi-database"></i>
            <h3>Keine gespeicherten PCAP-Dateien</h3>
            <p>Sie haben noch keine PCAP-Dateien in der Datenbank gespeichert.</p>
            <p>Erstellen Sie eine Topologie und speichern Sie die PCAP-Datei über den LabController.</p>
        </div>

        <div v-else class="pcaps-grid">
            <div 
                v-for="pcap in pcaps" 
                :key="pcap.id" 
                class="pcap-card"
            >
                <div class="pcap-header">
                    <div class="pcap-icon">
                        <i class="pi pi-file"></i>
                    </div>
                    <div class="pcap-info">
                        <h4>{{ pcap.topology_name }}</h4>
                        <p class="pcap-filename">{{ pcap.filename }}</p>
                    </div>
                </div>

                <div class="pcap-details">
                    <div class="detail-row">
                        <span class="label">Topologie:</span>
                        <span class="value">{{ pcap.topology_type }}</span>
                    </div>
                    <div class="detail-row">
                        <span class="label">Knoten:</span>
                        <span class="value">{{ pcap.node_count }}</span>
                    </div>
                    <div class="detail-row">
                        <span class="label">Größe:</span>
                        <span class="value">{{ formatFileSize(pcap.file_size) }}</span>
                    </div>
                    <div class="detail-row">
                        <span class="label">Erstellt:</span>
                        <span class="value">{{ formatDate(pcap.created_at) }}</span>
                    </div>
                </div>

                <div class="pcap-actions">
                    <Button
                        label="Herunterladen"
                        icon="pi pi-download"
                        size="small"
                        @click="downloadPcap(pcap.id, pcap.filename)"
                        class="download-btn"
                    />
                    <Button
                        label="Löschen"
                        icon="pi pi-trash"
                        size="small"
                        severity="danger"
                        @click="deletePcap(pcap.id)"
                        class="delete-btn"
                    />
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import Button from 'primevue/button';
import { useToast } from 'primevue/usetoast';

export default {
    name: 'SavedPcaps',
    components: {
        Button
    },
    setup() {
        const toast = useToast();
        return { toast };
    },
    data() {
        return {
            pcaps: [],
            loading: true
        };
    },
    async mounted() {
        await this.loadPcaps();
    },
    methods: {
        async loadPcaps() {
            try {
                this.loading = true;
                const userId = this.$store.state.user.id || 'guest';
                
                const response = await this.$axios.get(`/pcaps/${userId}`);
                
                if (response.data.status === 'success') {
                    this.pcaps = response.data.pcaps;
                } else {
                    throw new Error(response.data.message || 'Failed to load PCAPs');
                }
            } catch (error) {
                console.error('Error loading PCAPs:', error);
                this.toast.add({
                    severity: 'error',
                    summary: 'Fehler',
                    detail: 'Gespeicherte PCAP-Dateien konnten nicht geladen werden.',
                    life: 5000
                });
            } finally {
                this.loading = false;
            }
        },

        async downloadPcap(pcapId, filename) {
            try {
                const response = await this.$axios.get(`/pcap/${pcapId}/download`, {
                    responseType: 'blob'
                });
                
                // Create download link
                const blob = new Blob([response.data], { 
                    type: 'application/vnd.tcpdump.pcap' 
                });
                const url = window.URL.createObjectURL(blob);
                const link = document.createElement('a');
                link.href = url;
                link.download = filename;
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
                window.URL.revokeObjectURL(url);
                
                this.toast.add({
                    severity: 'success',
                    summary: 'Download',
                    detail: 'PCAP-Datei wurde erfolgreich heruntergeladen',
                    life: 3000
                });
            } catch (error) {
                console.error('Error downloading PCAP:', error);
                this.toast.add({
                    severity: 'error',
                    summary: 'Download Fehler',
                    detail: 'PCAP-Datei konnte nicht heruntergeladen werden',
                    life: 5000
                });
            }
        },

        async deletePcap(pcapId) {
            try {
                const userId = this.$store.state.user.id || 'guest';
                
                const response = await this.$axios.delete(`/pcap/${pcapId}?user_id=${userId}`);
                
                if (response.data.status === 'success') {
                    // Remove from local list
                    this.pcaps = this.pcaps.filter(pcap => pcap.id !== pcapId);
                    
                    this.toast.add({
                        severity: 'success',
                        summary: 'Gelöscht',
                        detail: 'PCAP-Datei wurde erfolgreich gelöscht',
                        life: 3000
                    });
                } else {
                    throw new Error(response.data.message || 'Failed to delete PCAP');
                }
            } catch (error) {
                console.error('Error deleting PCAP:', error);
                this.toast.add({
                    severity: 'error',
                    summary: 'Löschfehler',
                    detail: 'PCAP-Datei konnte nicht gelöscht werden',
                    life: 5000
                });
            }
        },

        formatFileSize(bytes) {
            if (bytes === 0) return '0 Bytes';
            const k = 1024;
            const sizes = ['Bytes', 'KB', 'MB', 'GB'];
            const i = Math.floor(Math.log(bytes) / Math.log(k));
            return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
        },

        formatDate(dateString) {
            if (!dateString) return 'Unbekannt';
            const date = new Date(dateString);
            return date.toLocaleDateString('de-DE', {
                year: 'numeric',
                month: '2-digit',
                day: '2-digit',
                hour: '2-digit',
                minute: '2-digit'
            });
        }
    }
};
</script>

<style scoped>
.saved-pcaps {
    padding: 2rem;
    max-width: 1200px;
    margin: 0 auto;
}

.header-section {
    text-align: center;
    margin-bottom: 2rem;
}

.header-section h2 {
    color: var(--nlb-text-primary);
    margin-bottom: 0.5rem;
}

.header-section p {
    color: var(--nlb-text-secondary);
    margin: 0;
}

.loading-section {
    text-align: center;
    padding: 3rem;
}

.loading-spinner {
    border: 4px solid var(--nlb-border-light);
    border-top: 4px solid var(--nlb-primary);
    border-radius: 50%;
    width: 40px;
    height: 40px;
    animation: spin 1s linear infinite;
    margin: 0 auto 1rem;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

.empty-state {
    text-align: center;
    padding: 3rem;
    color: var(--nlb-text-secondary);
}

.empty-state i {
    font-size: 3rem;
    margin-bottom: 1rem;
    opacity: 0.5;
}

.empty-state h3 {
    color: var(--nlb-text-primary);
    margin-bottom: 0.5rem;
}

.empty-state p {
    margin: 0.5rem 0;
}

.pcaps-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
    gap: 1.5rem;
}

.pcap-card {
    background: var(--nlb-bg-primary);
    border-radius: 12px;
    padding: 1.5rem;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    transition: all 0.3s ease;
}

.pcap-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
}

.pcap-header {
    display: flex;
    align-items: center;
    margin-bottom: 1rem;
}

.pcap-icon {
    background: var(--nlb-gradient-accent);
    width: 50px;
    height: 50px;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-right: 1rem;
}

.pcap-icon i {
    color: var(--nlb-text-light);
    font-size: 1.5rem;
}

.pcap-info h4 {
    color: var(--nlb-text-primary);
    margin: 0 0 0.25rem 0;
    font-size: 1.1rem;
}

.pcap-filename {
    color: var(--nlb-text-secondary);
    margin: 0;
    font-size: 0.9rem;
}

.pcap-details {
    margin-bottom: 1.5rem;
}

.detail-row {
    display: flex;
    justify-content: space-between;
    margin-bottom: 0.5rem;
}

.detail-row .label {
    color: var(--nlb-text-secondary);
    font-size: 0.9rem;
}

.detail-row .value {
    color: var(--nlb-text-primary);
    font-weight: 500;
    font-size: 0.9rem;
}

.pcap-actions {
    display: flex;
    gap: 0.75rem;
}

.download-btn {
    flex: 1;
}

.delete-btn {
    flex: 1;
}

@media (max-width: 768px) {
    .saved-pcaps {
        padding: 1rem;
    }
    
    .pcaps-grid {
        grid-template-columns: 1fr;
        gap: 1rem;
    }
    
    .pcap-card {
        padding: 1rem;
    }
    
    .pcap-actions {
        flex-direction: column;
    }
}
</style> 