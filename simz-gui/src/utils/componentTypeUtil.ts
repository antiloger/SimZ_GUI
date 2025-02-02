export function updateKey<T extends Record<string, any>>(
  obj: T,
  key: string, // Dynamic key input
  value: unknown
): T {
  if (!(key in obj)) {
    throw new Error(`Key "${key}" does not exist in the object.`);
  }

  const typedKey = key as keyof T; // Ensuring TypeScript recognizes the key

  if (typeof value !== typeof obj[typedKey]) {
    throw new TypeError(
      `Type mismatch for key "${key}". Expected "${typeof obj[typedKey]}", but got "${typeof value}".`
    );
  }

  return { ...obj, [typedKey]: value };
}
