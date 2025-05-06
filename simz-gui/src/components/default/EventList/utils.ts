import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatTimeValue(value: number, unit: string): string {
  // Format the time value with its unit
  return `${value} ${unit}`
}
