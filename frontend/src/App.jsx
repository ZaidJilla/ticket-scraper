import { useState } from "react"
import SearchBar from "./components/SearchBar"
import MonitorConfig from "./components/MonitorConfig"

function App() {
  const [results, setResults] = useState([])
  const [events, setEvents] = useState([])
  const [selectedPerformer, setSelectedPerformer] = useState(null)
  const [selectedShow, setSelectedShow] = useState(null)
  const [loading, setLoading] = useState(false)

  async function handleSearch(query) {
    setLoading(true)
    setEvents([])
    setSelectedShow(null)

    const searchResponse = await fetch(
      `https://mobile.gametime.co/v1/search?q=${encodeURIComponent(query)}`
    )
    const searchData = await searchResponse.json()
    const topResult = searchData.events?.[0]

    if (!topResult) {
      setLoading(false)
      return
    }

    setSelectedPerformer(topResult.event.name)
    const slug = topResult.performers[0]?.slug

    const eventsResponse = await fetch(
      `https://mobile.gametime.co/v1/events?page=1&per_page=100&performer_slug=${slug}`
    )
    const eventsData = await eventsResponse.json()
    setEvents(eventsData.events || [])
    setLoading(false)
  }

  async function handleSelectEvent(item) {
    setSelectedPerformer(item.event.name)
    setLoading(true)
    const slug = item.performers[0]?.slug
    const response = await fetch(
      `https://mobile.gametime.co/v1/events?page=1&per_page=100&performer_slug=${slug}`
    )
    const data = await response.json()
    setEvents(data.events || [])
    setLoading(false)
  }

  function handleSelectShow(item) {
    setSelectedShow(item)
  }

  async function handleStartMonitoring(config) {
    console.log("Starting monitoring with config:", config)
    try {
        const response = await fetch("http://127.0.0.1:8000/api/monitor", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(config)
        })
        const data = await response.json()
        if (data.status === "started") {
            alert(`Monitoring started for ${config.eventName}!`)
        } else {
            alert("Already monitoring this event.")
        }
    } catch (e) {
        console.error(e)
        alert("Failed to connect to backend.")
    }
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
      <p className="text-gray-500 mb-6">Monitor floor ticket prices across multiple sites</p>

      {!selectedShow && <SearchBar onSearch={handleSearch} />}

      {loading && <p className="mt-6 text-gray-500">Loading...</p>}

      {selectedShow ? (
        <MonitorConfig
          event={selectedShow.event}
          venue={selectedShow.venue}
          onStart={handleStartMonitoring}
          onBack={() => setSelectedShow(null)}
        />
      ) : !loading && events.length === 0 && results.length > 0 ? (
        <div className="mt-6">
          <p className="text-sm text-gray-500 mb-2">Select an artist to see all shows</p>
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
      ) : !loading && events.length > 0 ? (
        <div className="mt-6">
          <div className="flex justify-between items-center mb-2">
            <p className="font-semibold text-lg">{selectedPerformer} — All Shows</p>
            <button
              onClick={() => setEvents([])}
              className="text-sm text-blue-500 hover:underline"
            >
              Back
            </button>
          </div>
          {events.map((item) => (
            <div
              key={item.event.id}
              onClick={() => handleSelectShow(item)}
              className="p-4 border rounded-lg mb-2 hover:border-blue-500 cursor-pointer transition-colors"
            >
              <div className="flex justify-between items-start">
                <div>
                  <p className="font-semibold">{item.venue?.name}</p>
                  <p className="text-gray-500 text-sm">{item.venue?.city}, {item.venue?.state}</p>
                  <p className="text-gray-500 text-sm">{formatDate(item.event.datetime_local)}</p>
                </div>
                <p className="text-green-600 font-semibold">
                  {item.event.min_price ? formatPrice(item.event.min_price.total) : "N/A"}
                </p>
              </div>
            </div>
          ))}
        </div>
      ) : null}
    </div>
  )
}

export default App