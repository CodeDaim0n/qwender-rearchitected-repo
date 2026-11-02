"""Compatibility entry point for the current editable repository figures."""
import sys
from design_repository_assets import main

if __name__ == '__main__':
    sys.argv = [sys.argv[0], '--render']
    main()
