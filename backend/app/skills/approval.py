"""
Skill Approval System
---------------------
Manages approval workflow for skills and agents.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime


class ApprovalManager:
    """Manages approval workflow for skills and agents."""
    
    def __init__(self):
        self.approval_path = Path(__file__).parent / "pending_approvals.json"
        self.pending: Dict[str, dict] = {}
        self._load_pending()
    
    def _load_pending(self):
        """Load pending approvals from disk."""
        if self.approval_path.exists():
            try:
                self.pending = json.loads(self.approval_path.read_text())
                print(f"✅ Loaded {len(self.pending)} pending approvals")
            except Exception as e:
                print(f"❌ Failed to load pending approvals: {e}")
                self.pending = {}
    
    def _save_pending(self):
        """Save pending approvals to disk."""
        try:
            self.approval_path.write_text(json.dumps(self.pending, indent=2))
            print(f"✅ Saved {len(self.pending)} pending approvals")
        except Exception as e:
            print(f"❌ Failed to save pending approvals: {e}")
    
    def request_approval(
        self,
        item_type: str,
        item_name: str,
        config: dict,
        reason: str = ""
    ) -> str:
        """
        Request approval for a skill or agent.
        
        Args:
            item_type: Type of item (skill, agent)
            item_name: Name of item
            config: Item configuration
            reason: Reason for approval request
            
        Returns:
            Approval request ID
        """
        request_id = f"{item_type}_{item_name}_{datetime.now().timestamp()}"
        
        self.pending[request_id] = {
            "type": item_type,
            "name": item_name,
            "config": config,
            "reason": reason,
            "requested_at": datetime.now().isoformat(),
            "status": "pending"
        }
        
        self._save_pending()
        print(f"✅ Approval requested: {request_id}")
        return request_id
    
    def approve(self, request_id: str, approver: str = "system") -> bool:
        """
        Approve a pending request.
        
        Args:
            request_id: Request ID
            approver: Who approved it
            
        Returns:
            True if approved, False if not found
        """
        if request_id not in self.pending:
            print(f"❌ Approval request not found: {request_id}")
            return False
        
        self.pending[request_id]["status"] = "approved"
        self.pending[request_id]["approved_at"] = datetime.now().isoformat()
        self.pending[request_id]["approved_by"] = approver
        
        self._save_pending()
        print(f"✅ Approved: {request_id} by {approver}")
        return True
    
    def reject(self, request_id: str, reason: str = "", rejector: str = "system") -> bool:
        """
        Reject a pending request.
        
        Args:
            request_id: Request ID
            reason: Rejection reason
            rejector: Who rejected it
            
        Returns:
            True if rejected, False if not found
        """
        if request_id not in self.pending:
            print(f"❌ Approval request not found: {request_id}")
            return False
        
        self.pending[request_id]["status"] = "rejected"
        self.pending[request_id]["rejected_at"] = datetime.now().isoformat()
        self.pending[request_id]["rejected_by"] = rejector
        self.pending[request_id]["rejection_reason"] = reason
        
        self._save_pending()
        print(f"✅ Rejected: {request_id} by {rejector}")
        return True
    
    def get_pending(self) -> List[dict]:
        """
        Get all pending approval requests.
        
        Returns:
            List of pending requests
        """
        return [
            {"id": req_id, **req_data}
            for req_id, req_data in self.pending.items()
            if req_data.get("status") == "pending"
        ]
    
    def get_request(self, request_id: str) -> Optional[dict]:
        """
        Get a specific approval request.
        
        Args:
            request_id: Request ID
            
        Returns:
            Request data or None
        """
        if request_id in self.pending:
            return {"id": request_id, **self.pending[request_id]}
        return None
    
    def clear_old_requests(self, days: int = 30):
        """
        Clear old approval requests.
        
        Args:
            days: Age threshold in days
        """
        from datetime import timedelta
        
        cutoff = datetime.now() - timedelta(days=days)
        to_remove = []
        
        for req_id, req_data in self.pending.items():
            requested_at = datetime.fromisoformat(req_data["requested_at"])
            if requested_at < cutoff and req_data["status"] != "pending":
                to_remove.append(req_id)
        
        for req_id in to_remove:
            del self.pending[req_id]
        
        if to_remove:
            self._save_pending()
            print(f"✅ Cleared {len(to_remove)} old approval requests")


# Singleton instance
approval_manager = ApprovalManager()

