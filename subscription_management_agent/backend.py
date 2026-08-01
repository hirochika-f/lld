from __future__ import annotations

from models import Plan, Subscription, ToolCall


class SubscriptionBackend:
    def __init__(
        self,
        subscriptions: list[Subscription],
        plans: list[Plan],
        eligible_pairs: set[tuple[str, str]],
    ) -> None:
        self._subscriptions = {
            subscription.customer_id: subscription for subscription in subscriptions
        }
        self._plans = {plan.plan_id: plan for plan in plans}
        self._eligible_pairs = set(eligible_pairs)
        self._tool_calls: list[ToolCall] = []

    def get_plan(self, plan_id: str) -> Plan:
        return self._plans[plan_id]

    def is_eligible(self, customer_id: str, plan_id: str) -> bool:
        return (customer_id, plan_id) in self._eligible_pairs

    def get_subscription(self, customer_id: str) -> Subscription:
        return self._subscriptions[customer_id]

    def change_subscription(
        self,
        *,
        action_id: str,
        customer_id: str,
        target_plan_id: str,
    ) -> Subscription:
        self.get_plan(target_plan_id)
        subscription = self.get_subscription(customer_id)
        call = ToolCall(
            action_id=action_id,
            customer_id=customer_id,
            target_plan_id=target_plan_id,
        )
        self._tool_calls.append(call)
        subscription.plan_id = target_plan_id
        return subscription

    def get_tool_calls(
        self,
        *,
        action_id: str | None = None,
        customer_id: str | None = None,
    ) -> list[ToolCall]:
        calls = self._tool_calls
        if action_id is not None:
            calls = [call for call in calls if call.action_id == action_id]
        if customer_id is not None:
            calls = [call for call in calls if call.customer_id == customer_id]
        return list(calls)
