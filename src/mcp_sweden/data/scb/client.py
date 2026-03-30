"""HTTP client for the SCB API.

API base: https://api.scb.se/OV0104/v1/doris
Documentation: https://www.scb.se/vara-tjanster/oppna-data/api-for-statistikdatabasen/

Key endpoints:
    - Navigation: GET /sv/ssd/ (browse table hierarchy)
    - Table metadata: GET /sv/ssd/{table_id}
    - Query data: POST /sv/ssd/{table_id} (with JSON query body)
"""

from __future__ import annotations

# TODO: Implement API client functions
