import { useState } from "react"
import SearchBar from "./components/SearchBar"

function App() {
  const [results, setResults] = useState([])
  const [events, setEvents] = useState([])
  const [selectedPerformer, setSelectedPerformer] = useState(null)
  const [loading, setLoading] = useState(false)

  async function handleSearch(query) {
    setLoading(true)
    setEvents([])
    setSelectedPerformer(null)
    const response = await fetch(
      `https://mobile.gametime.co/v1/search?q=${encodeURIComponent(query)}`
    )
    const data = await response.json()
    setResults(data.events || [])
    setLoading(false)
  }

  async function handleSelectEvent(event) {
    setSelectedPerformer(event.event.name)
    setLoading(true)
    const performerId = event.performers[0]?.id
    const response = await fetch(
      `https://mobile.gametime.co/v1/events?page=1&per_page=100&performers[]=${performerId}`
    )
    const data = await response.json()
    setEvents(data.events || [])
    setLoading(false)
  }

  function formatDate(datetime) {
    const date = new Date(datetime)
    return date.toLocaleDateString("en-US", {
      weekday: "short",
      month: "short",
      day: "numeric",
      year: "numeric",
    })
  }

  function formatPrice(cents) {
    return `$${(cents / 100).toFixed(0)}+`
  }

  return (
    <div className="max-w-2xl mx-auto p-8">
      <h1 className="text-3xl font-bold mb-2">Ticket Scraper</h1>
      <p className="text-gray-500 mb-6">Search for an artist and monitor floor ticket prices</p>
      <SearchBar onSearch={handleSearch} />

      {loading && <p className="mt-6 text-gray-500">Loading...</p>}

      {!loading && events.length === 0 && results.length > 0 && (
        <div className="mt-6">
          <p className="text-sm text-gray-500 mb-2">Select a show to see all dates</p>
          {results.map((item) => (
            <div
              key={item.event.id}
              onClick={() => handleSelectEvent(item)}
              className="p-4 border rounded-lg mb-2 hover:border-blue-500 cursor-pointer transition-colors"
            >
              <div className="flex justify-between items-start">
                <div>
                  <p className="font-semibold text-lg">{item.event.name}</p>
                  <p className="text-gray-500 text-sm">{item.venue.name} · {item.venue.city}, {item.venue.state}</p>
                  <p className="text-gray-500 text-sm">{formatDate(item.event.datetime_local)}</p>
                </div>
                <p className="text-green-600 font-semibold">
                  {formatPrice(item.event.min_price.total)}
                </p>
              </div>
            </div>
          ))}
        </div>
      )}

      {!loading && events.length > 0 && (
        <div className="mt-6">
          <div className="flex justify-between items-center mb-2">
            <p className="font-semibold text-lg">{selectedPerformer} — All Shows</p>
            <button
              onClick={() => { setEvents([]); }}
              className="text-sm text-blue-500 hover:underline"
            >
              Back
            </button>
          </div>
          {events.map((item) => (
            <div
              key={item.id}
              className="p-4 border rounded-lg mb-2 hover:border-blue-500 cursor-pointer transition-colors"
            >
              <div className="flex justify-between items-start">
                <div>
                  <p className="font-semibold">{item.venue?.name}</p>
                  <p className="text-gray-500 text-sm">{item.venue?.city}, {item.venue?.state}</p>
                  <p className="text-gray-500 text-sm">{formatDate(item.datetime_local)}</p>
                </div>
                <p className="text-green-600 font-semibold">
                  {item.min_price ? formatPrice(item.min_price.total) : "N/A"}
                </p>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default App