"use client";

import { useState } from "react";

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

function CopyButton({ text, label }: { text: string; label: string }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <button
      onClick={handleCopy}
      className="shrink-0 rounded-md border border-gray-300 bg-gray-50 px-3 py-1.5 text-xs font-medium text-gray-700 transition hover:bg-gray-100"
    >
      {copied ? "Copied!" : label}
    </button>
  );
}

export default function Home() {
  const totalTools = features.reduce((sum, f) => sum + f.tools.length, 0);
  const [activeTab, setActiveTab] = useState<"claude-code" | "claude-desktop">(
    "claude-code"
  );

  const claudeCodeCommand =
    "claude mcp add mcp-sweden --transport http https://sweden.mcp.namraks.com/mcp";

  const claudeDesktopConfig = `{
  "mcpServers": {
    "mcp-sweden": {
      "type": "http",
      "url": "https://sweden.mcp.namraks.com/mcp"
    }
  }
}`;

  return (
    <div className="min-h-screen bg-white">
      {/* Hero */}
      <header className="px-6 py-20 text-center">
        <div className="mx-auto max-w-3xl">
          <h1 className="mb-3 text-5xl font-bold tracking-tight text-gray-900">
            mcp-sweden{" "}
            <span className="inline-block">🇸🇪</span>
          </h1>
          <p className="mb-4 text-xl text-gray-600">
            Swedish open data for AI assistants
          </p>
          <p className="mx-auto mb-10 max-w-2xl text-base text-gray-500">
            An MCP server that connects AI assistants like Claude to Swedish
            government data, statistics, public transport, financial markets, and
            more — all through the{" "}
            <a
              href="https://modelcontextprotocol.io"
              className="text-blue-600 underline hover:text-blue-800"
            >
              Model Context Protocol
            </a>
            .
          </p>
          <p className="mb-10 text-sm font-medium text-gray-400">
            {features.length} data sources &middot; {totalTools} tools &middot;
            One MCP server
          </p>

          {/* Connect box */}
          <div className="mx-auto max-w-2xl rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
            <p className="mb-4 text-sm font-semibold uppercase tracking-wider text-gray-500">
              Get started
            </p>

            {/* Tabs */}
            <div className="mb-4 flex justify-center gap-1 rounded-lg bg-gray-100 p-1">
              <button
                onClick={() => setActiveTab("claude-code")}
                className={`rounded-md px-4 py-2 text-sm font-medium transition ${
                  activeTab === "claude-code"
                    ? "bg-white text-gray-900 shadow-sm"
                    : "text-gray-500 hover:text-gray-700"
                }`}
              >
                Claude Code
              </button>
              <button
                onClick={() => setActiveTab("claude-desktop")}
                className={`rounded-md px-4 py-2 text-sm font-medium transition ${
                  activeTab === "claude-desktop"
                    ? "bg-white text-gray-900 shadow-sm"
                    : "text-gray-500 hover:text-gray-700"
                }`}
              >
                Claude Desktop
              </button>
            </div>

            {activeTab === "claude-code" ? (
              <div>
                <p className="mb-3 text-sm text-gray-500">
                  Run this command in your terminal:
                </p>
                <div className="flex items-center gap-2 rounded-lg border border-gray-200 bg-gray-50 px-4 py-3">
                  <code className="flex-1 overflow-x-auto text-sm text-gray-800 font-mono">
                    {claudeCodeCommand}
                  </code>
                  <CopyButton text={claudeCodeCommand} label="Copy" />
                </div>
              </div>
            ) : (
              <div>
                <p className="mb-3 text-sm text-gray-500">
                  Add this to your Claude Desktop config file (
                  <code className="rounded bg-gray-100 px-1.5 py-0.5 text-xs font-mono">
                    claude_desktop_config.json
                  </code>
                  ):
                </p>
                <div className="relative rounded-lg border border-gray-200 bg-gray-50 p-4">
                  <pre className="overflow-x-auto text-sm text-gray-800 font-mono">
                    {claudeDesktopConfig}
                  </pre>
                  <div className="absolute right-3 top-3">
                    <CopyButton text={claudeDesktopConfig} label="Copy" />
                  </div>
                </div>
                <p className="mt-3 text-xs text-gray-400">
                  Config file location: macOS{" "}
                  <code className="rounded bg-gray-100 px-1 py-0.5 font-mono">
                    ~/Library/Application Support/Claude/claude_desktop_config.json
                  </code>
                  {" "}&middot; Windows{" "}
                  <code className="rounded bg-gray-100 px-1 py-0.5 font-mono">
                    %APPDATA%\Claude\claude_desktop_config.json
                  </code>
                </p>
              </div>
            )}

            <div className="mt-5 flex flex-wrap justify-center gap-3">
              <a
                href="https://github.com/Namraks-Labs/mcp-sweden"
                className="rounded-full border border-gray-200 bg-white px-5 py-2 text-sm font-medium text-gray-700 transition hover:bg-gray-50"
              >
                GitHub
              </a>
              <a
                href="https://github.com/Namraks-Labs/mcp-sweden#installation"
                className="rounded-full bg-[#006aa7] px-5 py-2 text-sm font-medium text-white transition hover:bg-[#005a8e]"
              >
                Run locally
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
              className="group rounded-xl border border-gray-200 bg-white p-6 transition hover:border-[#006aa7]/30 hover:shadow-md"
            >
              <div className="mb-4 flex items-center gap-3">
                <span className="text-3xl">{feature.emoji}</span>
                <div>
                  <h2 className="text-xl font-bold text-gray-900">
                    {feature.name}
                  </h2>
                  <p className="text-sm text-gray-500">
                    {feature.description}
                  </p>
                </div>
              </div>
              <p className="mb-3 font-mono text-xs text-gray-400">
                {feature.api}
              </p>
              <ul className="space-y-1.5">
                {feature.tools.map((tool) => {
                  const [name, desc] = tool.split(" — ");
                  return (
                    <li key={name} className="flex text-sm">
                      <code className="mr-2 shrink-0 text-[#006aa7] font-mono">
                        {name}
                      </code>
                      <span className="text-gray-500">{desc}</span>
                    </li>
                  );
                })}
              </ul>
            </div>
          ))}
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-gray-200 px-6 py-8 text-center text-sm text-gray-400">
        <p>
          Built by{" "}
          <a
            href="https://github.com/Namraks-Labs"
            className="underline hover:text-gray-600"
          >
            Namraks Labs
          </a>{" "}
          &middot; Open source under MIT &middot; Powered by{" "}
          <a
            href="https://modelcontextprotocol.io"
            className="underline hover:text-gray-600"
          >
            MCP
          </a>
        </p>
      </footer>
    </div>
  );
}
