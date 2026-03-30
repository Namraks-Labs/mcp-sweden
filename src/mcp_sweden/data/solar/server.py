"""Solar feature server — registers tools for solar energy data.

Tools:
  - solar_installations: Solar panel stats per municipality
  - solar_growth: Historical growth with YoY% and CAGR
  - solar_forecast: Weather-based generation forecast via SMHI
  - electricity_prices: Nord Pool day-ahead spot prices (SE1-SE4)
  - solar_revenue: Revenue estimate combining all three data sources
"""

from fastmcp import FastMCP

from mcp_sweden.data.solar.tools import (
    electricity_prices,
    solar_forecast,
    solar_growth,
    solar_installations,
    solar_revenue,
)

mcp = FastMCP("mcp-sweden-solar")

mcp.tool(tags={"solar", "energy", "installations"})(solar_installations)
mcp.tool(tags={"solar", "energy", "growth", "statistics"})(solar_growth)
mcp.tool(tags={"solar", "energy", "forecast", "weather", "smhi"})(solar_forecast)
mcp.tool(tags={"energy", "electricity", "prices", "nordpool"})(electricity_prices)
mcp.tool(tags={"solar", "energy", "revenue", "forecast"})(solar_revenue)
