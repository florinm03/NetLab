<!-- TODO: Muss gelöscht werden -->

<template>
    <div class="pcap-viewer p-m-4">
        <h2>PCAP/PCAP-NG Viewer (client-only)</h2>

        <input
            type="file"
            accept=".pcap,.pcapng"
            @change="onFileUpload"
            class="p-mb-4"
        />

        <DataTable
            v-if="packets.length"
            :value="packets"
            paginator
            :rows="10"
            class="card"
        >
            <Column header="#" :body="rowIndex" style="width: 3em" />
            <Column field="timestamp" header="Time" />
            <Column field="src" header="Source" />
            <Column field="dst" header="Destination" />
            <Column field="proto" header="Protocol" />
            <Column field="length" header="Length" />
            <Column header="Info" :body="infoCell" />
        </DataTable>
    </div>
</template>

<script setup>
import { ref } from "vue";

const packets = ref([]);

// ——— 1) Classic libpcap parser ———
function parsePcapClassic(buffer) {
    const view = new DataView(buffer);
    const magic = view.getUint32(0, false);
    let little = false,
        ns = false;

    switch (magic) {
        case 0xa1b2c3d4:
            little = false;
            ns = false;
            break; // BE μs
        case 0xd4c3b2a1:
            little = true;
            ns = false;
            break; // LE μs
        case 0xa1b23c4d:
            little = false;
            ns = true;
            break; // BE ns
        case 0x4d3cb2a1:
            little = true;
            ns = true;
            break; // LE ns
        default:
            throw new Error("Not classic PCAP");
    }

    let offset = 24;
    const out = [];
    while (offset + 16 <= view.byteLength) {
        const ts_sec = view.getUint32(offset, little);
        const ts_frac = view.getUint32(offset + 4, little);
        const incl = view.getUint32(offset + 8, little);
        offset += 16;
        if (offset + incl > view.byteLength) break;

        // to JS ms
        const ts = ns
            ? ts_sec * 1000 + ts_frac / 1e6
            : ts_sec * 1000 + ts_frac / 1e3;

        const data = new Uint8Array(buffer, offset, incl);
        out.push({ ts, data });
        offset += incl;
    }
    return out;
}

// ——— 2) PCAP-NG parser (only EPB blocks) ———
function parsePcapNg(buffer) {
    const view = new DataView(buffer);
    // byte-order magic at offset 8
    const bom_be = view.getUint32(8, false);
    const bom_le = view.getUint32(8, true);
    const little = bom_le === 0x1a2b3c4d;
    const big = bom_be === 0x1a2b3c4d;
    if (!little && !big) throw new Error("Not PCAP-NG");

    let offset = 0;
    const out = [];
    while (offset + 8 <= view.byteLength) {
        const type = view.getUint32(offset, little);
        const len = view.getUint32(offset + 4, little);
        if (len < 8) break;

        // 0x00000006 = Enhanced Packet Block
        if (type === 0x00000006 && offset + 28 <= view.byteLength) {
            const th = view.getUint32(offset + 12, little);
            const tl = view.getUint32(offset + 16, little);
            const capLen = view.getUint32(offset + 20, little);
            const dataOff = offset + 28;
            if (dataOff + capLen <= view.byteLength) {
                // tsHigh*1000 + tsLow/1000 → ms
                const ts = th * 1000 + tl / 1000;
                const data = new Uint8Array(buffer, dataOff, capLen);
                out.push({ ts, data });
            }
        }

        offset += len;
    }
    return out;
}

// ——— 3) Universal dispatcher ———
function parseBuffer(buffer) {
    // try classic first
    try {
        return parsePcapClassic(buffer);
    } catch {
        // fallback to NG
        return parsePcapNg(buffer);
    }
}

// ——— 4) Lenient IPv4 finder + TCP/UDP dissection ———
function decodePacket({ data }) {
    const bytes = new Uint8Array(data.buffer, data.byteOffset, data.byteLength);

    // scan for IPv4 header in first 64 bytes
    let ipOff = -1;
    for (let i = 0; i < Math.min(64, bytes.length); i++) {
        const version = bytes[i] >> 4;
        const ihl = bytes[i] & 0x0f;
        if (version === 4 && ihl >= 5 && i + ihl * 4 <= bytes.length) {
            ipOff = i;
            break;
        }
    }
    if (ipOff < 0) return { proto: "Unknown", src: "", dst: "" };

    const ihl = (bytes[ipOff] & 0x0f) * 4;
    const protoNum = bytes[ipOff + 9];
    const sip = Array.from(bytes.slice(ipOff + 12, ipOff + 16)).join(".");
    const dip = Array.from(bytes.slice(ipOff + 16, ipOff + 20)).join(".");

    let proto, src, dst;
    if (protoNum === 6 || protoNum === 17) {
        proto = protoNum === 6 ? "TCP" : "UDP";
        const b = ipOff + ihl;
        const sport = (bytes[b] << 8) + bytes[b + 1];
        const dport = (bytes[b + 2] << 8) + bytes[b + 3];
        src = `${sip}:${sport}`;
        dst = `${dip}:${dport}`;
    } else {
        proto = `IP(${protoNum})`;
        src = sip;
        dst = dip;
    }

    return { proto, src, dst };
}

// ——— 5) Table helpers ———
function rowIndex(_, p) {
    return p.rowIndex + 1;
}
function infoCell(r) {
    return `${r.proto} ${r.src} → ${r.dst}`;
}

// ——— 6) File-picker handler ———
async function onFileUpload(ev) {
    const file = ev.target.files[0];
    if (!file) return;
    packets.value = [];

    const buf = await file.arrayBuffer();
    let recs;
    try {
        recs = parseBuffer(buf);
    } catch (e) {
        return alert(`Parse error: ${e.message}`);
    }

    recs.forEach(({ ts, data }) => {
        const { proto, src, dst } = decodePacket({ data });
        packets.value.push({
            timestamp: new Date(ts).toLocaleString(),
            src,
            dst,
            proto,
            length: data.byteLength,
        });
    });
}
</script>

<style scoped>
.card {
    display: flex;
    flex-direction: column;
}
.p-m-4 {
    margin: 1rem;
}
.p-mb-4 {
    margin-bottom: 1rem;
}
</style>
