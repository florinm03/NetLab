<template>
    <div class="card">
        <iframe
            src="http://localhost:7681"
            frameborder="0"
            class="terminal-container"
        ></iframe>
    </div>
</template>

<script>
export default {
    
    mounted() {
        window.addEventListener("resize", this.resizeTerminal);
        this.resizeTerminal();
    },
    methods: {
        resizeTerminal() {
            const iframe = document.querySelector(".terminal-frame");
            iframe.style.height = `${window.innerHeight - 50}px`;
        },
    },
};
</script>

<style>
.terminal-container {
    width: 100%;
    height: 20vh;
}
</style>
