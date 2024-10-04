"""Context manager for basic directory watching.

Includes a workaround for <https://github.com/gorakhargosh/watchdog/issues/346>.
"""

from datetime import datetime, timedelta
from pathlib import Path
from time import sleep
from typing import Callable, Self

from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer


class DirWatcher:
    """Run a function when a directory changes."""

    def __init__(
        self,
        watch_dir: Path,
        on_created: Callable[[FileSystemEvent], None],
    ):
        self.watch_dir = watch_dir
        self.on_created = on_created

    def __enter__(self) -> Self:
        self.observer = Observer()
        self.observer.schedule(
            CreatedFileHandler(self.on_created), self.watch_dir
        )
        self.observer.start()
        return self

    def __exit__(self, exc_type: Exception | None, *_) -> bool:
        if exc_type and exc_type is KeyboardInterrupt:
            self.observer.stop()
            handled_exception = True
        elif exc_type:
            handled_exception = False
        else:
            handled_exception = True
        self.observer.join()
        return handled_exception

    def run(self):
        """Check for changes on an interval."""
        while True:
            sleep(self.interval)


class CreatedFileHandler(FileSystemEventHandler):
    """Handle modified files."""

    def __init__(self, func: Callable[[FileSystemEvent], None]):
        self.func = func
        
    def on_created(self, event: FileSystemEvent):

        self.func(event)