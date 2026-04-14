"""
Heartbeat Scheduler — Proactive task execution via cron patterns.

Loads scheduled jobs from config and runs skills at specified intervals.
"""

import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

logger = logging.getLogger("claudius.scheduler")


class Scheduler:
    """Cron-based scheduler for proactive Claudius tasks."""

    def __init__(self, config: dict, router):
        self.config = config
        self.router = router
        self.timezone = config.get("timezone", "America/New_York")
        self.scheduler = AsyncIOScheduler(timezone=self.timezone)

    def start(self):
        """Register all configured jobs and start the scheduler."""
        jobs = self.config.get("jobs", [])
        for job in jobs:
            if not job.get("enabled", True):
                continue
            cron_parts = job["cron"].split()
            trigger = CronTrigger(
                minute=cron_parts[0],
                hour=cron_parts[1],
                day=cron_parts[2],
                month=cron_parts[3],
                day_of_week=cron_parts[4],
                timezone=self.timezone,
            )
            self.scheduler.add_job(
                self._run_skill,
                trigger=trigger,
                args=[job["skill"], job["name"]],
                id=job["name"],
                name=job["name"],
            )
            logger.info(f"  Scheduled: {job['name']} → skill:{job['skill']} ({job['cron']})")

        self.scheduler.start()

    async def _run_skill(self, skill_name: str, job_name: str):
        """Execute a skill via the router."""
        logger.info(f"⏰ Scheduled job running: {job_name}")
        try:
            response = await self.router.handle(
                message=f"Run the '{skill_name}' skill now.",
                source="scheduler",
                metadata={"job": job_name, "skill": skill_name},
            )
            logger.info(f"  Job {job_name} complete ({len(response)} chars)")
        except Exception as e:
            logger.error(f"  Job {job_name} failed: {e}")

    def stop(self):
        """Stop the scheduler."""
        self.scheduler.shutdown(wait=False)
