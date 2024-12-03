/* prettier-ignore-start */

/* eslint-disable */

// @ts-nocheck

// noinspection JSUnusedGlobalSymbols

// This file is auto-generated by TanStack Router

import { createFileRoute } from '@tanstack/react-router'

// Import Routes

import { Route as rootRoute } from './routes/__root'
import { Route as IndexImport } from './routes/index'
import { Route as AppAppImport } from './routes/app/_app'
import { Route as authRegisterImport } from './routes/(auth)/register'
import { Route as authLoginImport } from './routes/(auth)/login'
import { Route as AppAppOverviewImport } from './routes/app/_app.overview'

// Create Virtual Routes

const AppImport = createFileRoute('/app')()

// Create/Update Routes

const AppRoute = AppImport.update({
  path: '/app',
  getParentRoute: () => rootRoute,
} as any)

const IndexRoute = IndexImport.update({
  path: '/',
  getParentRoute: () => rootRoute,
} as any)

const AppAppRoute = AppAppImport.update({
  id: '/_app',
  getParentRoute: () => AppRoute,
} as any)

const authRegisterRoute = authRegisterImport.update({
  path: '/register',
  getParentRoute: () => rootRoute,
} as any)

const authLoginRoute = authLoginImport.update({
  path: '/login',
  getParentRoute: () => rootRoute,
} as any)

const AppAppOverviewRoute = AppAppOverviewImport.update({
  path: '/overview',
  getParentRoute: () => AppAppRoute,
} as any)

// Populate the FileRoutesByPath interface

declare module '@tanstack/react-router' {
  interface FileRoutesByPath {
    '/': {
      id: '/'
      path: '/'
      fullPath: '/'
      preLoaderRoute: typeof IndexImport
      parentRoute: typeof rootRoute
    }
    '/(auth)/login': {
      id: '/(auth)/login'
      path: '/login'
      fullPath: '/login'
      preLoaderRoute: typeof authLoginImport
      parentRoute: typeof rootRoute
    }
    '/(auth)/register': {
      id: '/(auth)/register'
      path: '/register'
      fullPath: '/register'
      preLoaderRoute: typeof authRegisterImport
      parentRoute: typeof rootRoute
    }
    '/app': {
      id: '/app'
      path: '/app'
      fullPath: '/app'
      preLoaderRoute: typeof AppImport
      parentRoute: typeof rootRoute
    }
    '/app/_app': {
      id: '/app/_app'
      path: '/app'
      fullPath: '/app'
      preLoaderRoute: typeof AppAppImport
      parentRoute: typeof AppRoute
    }
    '/app/_app/overview': {
      id: '/app/_app/overview'
      path: '/overview'
      fullPath: '/app/overview'
      preLoaderRoute: typeof AppAppOverviewImport
      parentRoute: typeof AppAppImport
    }
  }
}

// Create and export the route tree

interface AppAppRouteChildren {
  AppAppOverviewRoute: typeof AppAppOverviewRoute
}

const AppAppRouteChildren: AppAppRouteChildren = {
  AppAppOverviewRoute: AppAppOverviewRoute,
}

const AppAppRouteWithChildren =
  AppAppRoute._addFileChildren(AppAppRouteChildren)

interface AppRouteChildren {
  AppAppRoute: typeof AppAppRouteWithChildren
}

const AppRouteChildren: AppRouteChildren = {
  AppAppRoute: AppAppRouteWithChildren,
}

const AppRouteWithChildren = AppRoute._addFileChildren(AppRouteChildren)

export interface FileRoutesByFullPath {
  '/': typeof IndexRoute
  '/login': typeof authLoginRoute
  '/register': typeof authRegisterRoute
  '/app': typeof AppAppRouteWithChildren
  '/app/overview': typeof AppAppOverviewRoute
}

export interface FileRoutesByTo {
  '/': typeof IndexRoute
  '/login': typeof authLoginRoute
  '/register': typeof authRegisterRoute
  '/app': typeof AppAppRouteWithChildren
  '/app/overview': typeof AppAppOverviewRoute
}

export interface FileRoutesById {
  __root__: typeof rootRoute
  '/': typeof IndexRoute
  '/(auth)/login': typeof authLoginRoute
  '/(auth)/register': typeof authRegisterRoute
  '/app': typeof AppRouteWithChildren
  '/app/_app': typeof AppAppRouteWithChildren
  '/app/_app/overview': typeof AppAppOverviewRoute
}

export interface FileRouteTypes {
  fileRoutesByFullPath: FileRoutesByFullPath
  fullPaths: '/' | '/login' | '/register' | '/app' | '/app/overview'
  fileRoutesByTo: FileRoutesByTo
  to: '/' | '/login' | '/register' | '/app' | '/app/overview'
  id:
    | '__root__'
    | '/'
    | '/(auth)/login'
    | '/(auth)/register'
    | '/app'
    | '/app/_app'
    | '/app/_app/overview'
  fileRoutesById: FileRoutesById
}

export interface RootRouteChildren {
  IndexRoute: typeof IndexRoute
  authLoginRoute: typeof authLoginRoute
  authRegisterRoute: typeof authRegisterRoute
  AppRoute: typeof AppRouteWithChildren
}

const rootRouteChildren: RootRouteChildren = {
  IndexRoute: IndexRoute,
  authLoginRoute: authLoginRoute,
  authRegisterRoute: authRegisterRoute,
  AppRoute: AppRouteWithChildren,
}

export const routeTree = rootRoute
  ._addFileChildren(rootRouteChildren)
  ._addFileTypes<FileRouteTypes>()

/* prettier-ignore-end */

/* ROUTE_MANIFEST_START
{
  "routes": {
    "__root__": {
      "filePath": "__root.tsx",
      "children": [
        "/",
        "/(auth)/login",
        "/(auth)/register",
        "/app"
      ]
    },
    "/": {
      "filePath": "index.tsx"
    },
    "/(auth)/login": {
      "filePath": "(auth)/login.tsx"
    },
    "/(auth)/register": {
      "filePath": "(auth)/register.tsx"
    },
    "/app": {
      "filePath": "app",
      "children": [
        "/app/_app"
      ]
    },
    "/app/_app": {
      "filePath": "app/_app.tsx",
      "parent": "/app",
      "children": [
        "/app/_app/overview"
      ]
    },
    "/app/_app/overview": {
      "filePath": "app/_app.overview.tsx",
      "parent": "/app/_app"
    }
  }
}
ROUTE_MANIFEST_END */
