#!/usr/bin/env python3
"""
SimZ Engine - Socket.IO Server
This is a standalone server that provides Socket.IO API for the SimZ Engine

Environment Variables:
- SIMZ_HOST: Host address to bind to (default: 0.0.0.0)
- SIMZ_PORT: Port to listen on (default: 5000)
- SIMZ_PROJECT_DIR: Directory where projects are stored (default: ./projects)
- SIMZ_DEBUG: Enable debug mode (default: False)
- SIMZ_CORS_ALLOWED_ORIGINS: CORS allowed origins (default: *)
"""

import os
import argparse
from src.core.project_manager import ProjectManager
from src.core.socket_manager import SocketManager
from src.utils.env_manager import env_manager


def main():
    """Main function for the Socket.IO server"""
    parser = argparse.ArgumentParser(description="SimZ Engine - Socket.IO Server")
    parser.add_argument(
        "--host", type=str, help="Host address to bind to (overrides SIMZ_HOST)"
    )
    parser.add_argument(
        "--port", type=int, help="Port to listen on (overrides SIMZ_PORT)"
    )
    parser.add_argument(
        "--project-dir",
        type=str,
        help="Directory where projects are stored (overrides SIMZ_PROJECT_DIR)",
    )
    parser.add_argument(
        "--debug", action="store_true", help="Enable debug mode (overrides SIMZ_DEBUG)"
    )
    args = parser.parse_args()

    # Update environment configuration with command-line arguments
    if args.host:
        env_manager.set("HOST", args.host)
    if args.port:
        env_manager.set("PORT", args.port)
    if args.project_dir:
        env_manager.set("PROJECT_DIR", args.project_dir)
    if args.debug:
        env_manager.set("DEBUG", True)

    # Print current configuration
    env_manager.print_config()

    # Create ProjectManager with project directory from config
    project_dir = env_manager.get("PROJECT_DIR")
    comp_reg_dir = env_manager.get("COMP_REG_DIR")
    project_manager = ProjectManager(comp_reg_dir=comp_reg_dir, base_dir=project_dir)
    print(f"Project manager initialized with base directory: {project_dir}")

    # Create SocketManager
    socket_manager = SocketManager(project_manager)

    print(
        f"Starting Socket.IO server on {env_manager.get('HOST')}:{env_manager.get('PORT')}"
    )
    print("Press Ctrl+C to stop the server")

    try:
        # Run the server (configuration is already loaded by SocketManager)
        socket_manager.run()
    except KeyboardInterrupt:
        print("Server stopped")


if __name__ == "__main__":
    main()
