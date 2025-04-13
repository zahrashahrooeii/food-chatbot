"""
Compatibility middleware for Python 3.12 and Django REST Framework
"""
import pkgutil
import sys
import logging
import importlib.abc

logger = logging.getLogger(__name__)

class PatchingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        
        # Apply ImpImporter patch for Python 3.12 compatibility
        if not hasattr(pkgutil, 'ImpImporter'):
            # Create a dummy ImpImporter class
            class ImpImporter(importlib.abc.MetaPathFinder):
                def __init__(self, *args, **kwargs):
                    pass
                
                def find_module(self, fullname, path=None):
                    return None
            
            # Add it to pkgutil
            pkgutil.ImpImporter = ImpImporter
            logger.info("Applied patch for pkgutil.ImpImporter in Python 3.12")
        
        # Apply patches for DRF templatetags
        try:
            from rest_framework import compat
            if not hasattr(compat, 'apply_markdown'):
                # Add dummy apply_markdown function to DRF compat
                def dummy_apply_markdown(text):
                    return text
                
                compat.apply_markdown = dummy_apply_markdown
                logger.info("Applied patch for missing apply_markdown in DRF")
                
            if not hasattr(compat, 'pygments_highlight'):
                # Add dummy pygments_highlight function to DRF compat
                def dummy_pygments_highlight(text, lexer, formatter):
                    return text
                
                compat.pygments_highlight = dummy_pygments_highlight
                logger.info("Applied patch for missing pygments_highlight in DRF")
        except ImportError:
            # If we can't import compat, no need to patch it
            pass

    def __call__(self, request):
        # Process the request normally
        response = self.get_response(request)
        return response 