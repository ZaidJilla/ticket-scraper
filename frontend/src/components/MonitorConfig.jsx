import { useState } from "react"

function MonitorConfig({ event, venue, onStart, onBack }) {
    const [priceThreshold, setPriceThreshold] = useState(500)
    const [minQuantity, setMinQuantity] = useState(4)
    const [webhook, setWebhook] = useState("")
    const [mention, setMention] = useState("@everyone")

    function formatDate(datetime) {
        const date = new Date(datetime)
        return date.toLocaleDateString("en-US", {
            weekday: "short",
            month: "short",
            day: "numeric",
            year: "numeric",
        })
    }

    function handleStart() {
        if (!webhook.trim()) {
            alert("Please enter a Discord webhook URL")
            return
        }
        onStart({
            eventId: event.id,
            eventName: event.name,
            venue: venue.name,
            city: venue.city,
            state: venue.state,
            date: event.datetime_local,
            priceThreshold,
            minQuantity,
            webhook,
            mention,
        })
    }

    return (
    <div>
      <button
        onClick={onBack}
        className="text-sm text-blue-500 hover:underline mb-4 block"
      >
        ← Back to shows
      </button>

      <div className="p-4 bg-gray-50 rounded-lg mb-6">
        <p className="font-semibold text-lg">{event.name}</p>
        <p className="text-gray-500 text-sm">{venue.name} · {venue.city}, {venue.state}</p>
        <p className="text-gray-500 text-sm">{formatDate(event.datetime_local)}</p>
      </div>

      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium mb-1">Max Price ($)</label>
          <input
            type="number"
            value={priceThreshold}
            onChange={(e) => setPriceThreshold(Number(e.target.value))}
            className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:border-blue-500"
          />
        </div>

        <div>
          <label className="block text-sm font-medium mb-1">Minimum Quantity</label>
          <input
            type="number"
            value={minQuantity}
            onChange={(e) => setMinQuantity(Number(e.target.value))}
            className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:border-blue-500"
          />
        </div>

        <div>
          <label className="block text-sm font-medium mb-1">Discord Webhook URL</label>
          <input
            type="text"
            value={webhook}
            onChange={(e) => setWebhook(e.target.value)}
            placeholder="https://discord.com/api/webhooks/..."
            className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:border-blue-500"
          />
        </div>

        <div>
          <label className="block text-sm font-medium mb-1">Discord Mention</label>
          <input
            type="text"
            value={mention}
            onChange={(e) => setMention(e.target.value)}
            placeholder="@everyone or <@USER_ID>"
            className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:border-blue-500"
          />
        </div>

        <button
          onClick={handleStart}
          className="w-full py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 font-medium"
        >
          Start Monitoring
        </button>
      </div>
    </div>
  )
}

export default MonitorConfig