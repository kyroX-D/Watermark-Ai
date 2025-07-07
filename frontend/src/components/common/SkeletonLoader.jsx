export default function SkeletonLoader({ className = "", count = 1 }) {
  return (
    <>
      {Array.from({ length: count }).map((_, i) => (
        <div
          key={i}
          className={`animate-pulse bg-gray-200 dark:bg-dark-border rounded ${className}`}
        />
      ))}
    </>
  );
}
