import { useState } from "react"

function SearchBar({ onSearch }) {
    const [query, setQuery] = useState("")

    function handleSubmit(e) {
        e.preventDefault()
        if (query.trim()) {
            onSearch(query)
        }
    }

    return (
        <form onSubmit={handleSubmit} className="flex gap-2">
            <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Search for an artist..."
                className="flex-1 px-4 py-2 rounded-lg border border-gray-300 focus:outline-none focus:border-blue-500"
            />
            <button
                type="submit"
                className="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600"
            >
                Search
            </button>
        </form>
    )
}

export default SearchBar