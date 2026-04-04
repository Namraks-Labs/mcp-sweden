const features = [
  {
    emoji: "🏛️",
    name: "Riksdag",
    description: "Parliament members, votes, documents & debates",
    api: "data.riksdagen.se",
    tools: [
      "search_documents — Search motions, propositions, reports",
      "list_members — Current parliament members by party",
      "get_member_details — Roles, assignments & history",
      "search_votes — Vote results with yes/no/abstain counts",
      "search_speeches — Debate contributions & speeches",
    ],
  },
  {
    emoji: "📊",
    name: "SCB",
    description: "Population, economy, labor & trade statistics",
    api: "api.scb.se",
    tools: [
      "scb_list_subjects — Browse all statistical subject areas",
      "scb_browse — Navigate the table hierarchy",
      "scb_table_info — Table metadata & available variables",
      "scb_query — Query data with filters & selections",
      "scb_search — Find tables by keyword",
    ],
  },
  {
    emoji: "🏘️",
    name: "Kolada",
    description: "Municipality & region KPIs and rankings",
    api: "api.kolada.se",
    tools: [
      "search_kpis — Find KPIs by keyword",
      "get_kpi_details — Full KPI metadata",
      "search_municipalities — Find municipalities & regions",
      "get_kpi_data — Values with gender breakdowns",
      "compare_municipalities — Benchmark across municipalities",
      "search_kpi_groups — Thematic KPI groups",
    ],
  },
  {
    emoji: "🎓",
    name: "Skolverket",
    description: "School registry, grades & teacher statistics",
    api: "api.skolverket.se",
    tools: [
      "list_municipalities — All municipalities with codes",
      "list_school_forms — School types in Sweden",
      "search_schools — Find schools by area & type",
      "get_school_detail — Contact info & education types",
      "get_school_statistics — Teacher ratios & certification",
      "find_schools_in_municipality — All schools in an area",
    ],
  },
  {
    emoji: "📻",
    name: "Sveriges Radio",
    description: "Channels, programs, episodes, news & traffic",
    api: "api.sr.se",
    tools: [
      "list_channels — All channels with live audio URLs",
      "get_schedule — Broadcast schedule for a channel",
      "search_programs — Find programs by name",
      "get_episodes — Episodes with audio URLs",
      "get_now_playing — Currently playing on a channel",
      "get_traffic_messages — Road incidents & delays",
    ],
  },
  {
    emoji: "📈",
    name: "Avanza",
    description: "Stock quotes, funds, orderbook & market data",
    api: "avanza.se",
    tools: [
      "search_instruments — Stocks, funds, indices",
      "get_stock_info — Price, P/E, dividend, 52-week data",
      "get_fund_info — NAV, fees, risk, top holdings",
      "get_price_chart — Historical OHLC price data",
      "get_orderbook_depth — Bid/ask levels & spread",
      "get_market_overview — Major indices & top movers",
    ],
  },
  {
    emoji: "🏢",
    name: "Bolagsverket",
    description: "Company search, registration & annual reports",
    api: "bolagsverket.se",
    tools: [
      "search_companies — Search by name or org number",
      "get_company_info — Registration, address, share capital",
      "get_company_officers — Board members, CEO, auditors",
      "get_company_events — Filings & registration changes",
    ],
  },
  {
    emoji: "♻️",
    name: "Begagnad",
    description: "Second-hand marketplaces — Blocket & Tradera",
    api: "blocket.se / tradera.com",
    tools: [
      "search_blocket — Listings with price & location",
      "get_blocket_item — Full listing details & images",
      "search_tradera — Auctions & buy-it-now listings",
      "search_begagnad — Search both platforms at once",
    ],
  },
  {
    emoji: "☀️",
    name: "Solar",
    description: "Solar energy production, irradiance & prices",
    api: "smhi.se / nordpool",
    tools: [
      "solar_installations — Stats by municipality & year",
      "solar_growth — Year-over-year growth & CAGR",
      "solar_forecast — Generation forecast with weather",
      "electricity_prices — Spot prices for SE1-SE4 zones",
      "solar_revenue — Revenue estimate combining all data",
    ],
  },
  {
    emoji: "🚇",
    name: "SL",
    description: "Stockholm public transport — real-time departures",
    api: "transport.integration.sl.se",
    tools: [
      "search_stations — Find stops by name",
      "get_departures — Real-time departures by mode",
      "list_lines — All lines grouped by type",
      "get_station_info — Station details & serving lines",
      "get_nearby_stations — Stations near a location",
    ],
  },
];

export default function Home() {
  const totalTools = features.reduce((sum, f) => sum + f.tools.length, 0);

  return (
    <div className="min-h-screen">
      {/* Hero */}
      <header className="relative overflow-hidden px-6 py-24 text-center">
        <div className="absolute inset-0 bg-gradient-to-b from-[#006aa7]/20 to-transparent" />
        <div className="relative mx-auto max-w-3xl">
          <h1 className="mb-2 text-6xl font-bold tracking-tight">
            mcp-sweden{" "}
            <span className="inline-block animate-pulse">🇸🇪</span>
          </h1>
          <p className="mb-6 text-xl text-blue-200">
            Swedish open data for AI assistants
          </p>
          <p className="mb-10 text-lg text-blue-300/80">
            {features.length} data sources &middot; {totalTools} tools &middot;
            One MCP server
          </p>

          {/* Connect box */}
          <div className="mx-auto max-w-2xl rounded-xl border border-white/10 bg-white/5 p-6 backdrop-blur">
            <p className="mb-3 text-sm font-medium uppercase tracking-wider text-blue-300">
              Connect now
            </p>
            <code className="block rounded-lg bg-black/40 px-4 py-3 text-sm text-[#FECC00] font-mono">
              claude mcp add mcp-sweden --transport http
              https://sweden.mcp.namraks.com/mcp
            </code>
            <div className="mt-4 flex flex-wrap justify-center gap-3">
              <a
                href="https://github.com/Namraks-Labs/mcp-sweden"
                className="rounded-full bg-white/10 px-5 py-2 text-sm font-medium transition hover:bg-white/20"
              >
                GitHub
              </a>
              <a
                href="https://github.com/Namraks-Labs/mcp-sweden#installation"
                className="rounded-full bg-[#FECC00] px-5 py-2 text-sm font-medium text-[#001845] transition hover:bg-[#ffd633]"
              >
                Install locally
              </a>
            </div>
          </div>
        </div>
      </header>

      {/* Features grid */}
      <main className="mx-auto max-w-6xl px-6 pb-24">
        <div className="grid gap-6 md:grid-cols-2">
          {features.map((feature) => (
            <div
              key={feature.name}
              className="group rounded-xl border border-white/10 bg-white/5 p-6 transition hover:border-[#FECC00]/30 hover:bg-white/[0.07]"
            >
              <div className="mb-4 flex items-center gap-3">
                <span className="text-3xl">{feature.emoji}</span>
                <div>
                  <h2 className="text-xl font-bold">{feature.name}</h2>
                  <p className="text-sm text-blue-300">{feature.description}</p>
                </div>
              </div>
              <p className="mb-3 font-mono text-xs text-blue-400">
                {feature.api}
              </p>
              <ul className="space-y-1.5">
                {feature.tools.map((tool) => {
                  const [name, desc] = tool.split(" — ");
                  return (
                    <li key={name} className="flex text-sm">
                      <code className="mr-2 shrink-0 text-[#FECC00]/80">
                        {name}
                      </code>
                      <span className="text-blue-200/60">{desc}</span>
                    </li>
                  );
                })}
              </ul>
            </div>
          ))}
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-white/10 px-6 py-8 text-center text-sm text-blue-300/50">
        <p>
          Built by{" "}
          <a
            href="https://github.com/Namraks-Labs"
            className="underline hover:text-blue-200"
          >
            Namraks Labs
          </a>{" "}
          &middot; Open source under MIT &middot; Powered by{" "}
          <a
            href="https://modelcontextprotocol.io"
            className="underline hover:text-blue-200"
          >
            MCP
          </a>
        </p>
      </footer>
    </div>
  );
}
