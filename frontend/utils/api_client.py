import requests
from typing import Optional, Dict, Any
import streamlit as st

class APIClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.timeout = 30
    
    def _request(self, method: str, endpoint: str, data: Optional[Dict] = None, params: Optional[Dict] = None) -> Optional[Dict]:
        """Make HTTP request to API"""
        url = f"{self.base_url}{endpoint}"
        try:
            response = requests.request(
                method=method,
                url=url,
                json=data,
                params=params,
                timeout=self.timeout
            )
            if response.status_code == 204:
                return {"success": True}
            response.raise_for_status()
            return response.json() if response.content else {"success": True}
        except requests.exceptions.ConnectionError:
            st.error("❌ Cannot connect to API. Please make sure the backend is running.")
            return None
        except requests.exceptions.Timeout:
            st.error("⏰ Request timeout. Please try again.")
            return None
        except requests.exceptions.HTTPError as e:
            if response.status_code == 404:
                st.warning("Resource not found.")
            else:
                st.error(f"❌ API Error: {e}")
            return None
        except Exception as e:
            st.error(f"❌ Unexpected error: {e}")
            return None
    
    def get_tasks(self, **params) -> Optional[list]:
        """Get tasks with filters"""
        return self._request("GET", "/tasks", params=params)
    
    def get_task(self, task_id: int) -> Optional[Dict]:
        """Get single task"""
        return self._request("GET", f"/tasks/{task_id}")
    
    def create_task(self, task_data: Dict) -> Optional[Dict]:
        """Create new task"""
        return self._request("POST", "/tasks", data=task_data)
    
    def update_task(self, task_id: int, task_data: Dict) -> Optional[Dict]:
        """Update task"""
        return self._request("PUT", f"/tasks/{task_id}", data=task_data)
    
    def delete_task(self, task_id: int) -> bool:
        """Delete task"""
        result = self._request("DELETE", f"/tasks/{task_id}")
        return result is not None
    
    def get_statistics(self) -> Optional[Dict]:
        """Get task statistics"""
        return self._request("GET", "/statistics")
    
    def get_overdue_tasks(self) -> Optional[list]:
        """Get overdue tasks"""
        return self._request("GET", "/tasks/overdue")
    
    def get_due_soon_tasks(self, hours: int = 24) -> Optional[list]:
        """Get tasks due soon"""
        return self._request("GET", "/tasks/due-soon", params={"hours": hours})
    
    def add_comment(self, task_id: int, comment: str, created_by: str = None) -> Optional[Dict]:
        """Add comment to task"""
        data = {"task_id": task_id, "comment": comment, "created_by": created_by}
        return self._request("POST", "/comments", data=data)
    
    def get_comments(self, task_id: int) -> Optional[list]:
        """Get task comments"""
        return self._request("GET", f"/tasks/{task_id}/comments")
    
    def health_check(self) -> bool:
        """Check if API is healthy"""
        result = self._request("GET", "/health")
        return result is not None and result.get("status") == "healthy"

# Global API client instance
api_client = APIClient()