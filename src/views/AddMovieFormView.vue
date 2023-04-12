<template>
    <div>
        <h1> Add New Movie</h1>
        <MovieForm />
    </div>
    </template>
    
    <script>
    import MovieForm from '@/components/MovieForm.vue'
    
    export default {
    components: {
        MovieForm
    }
    }
    </script>