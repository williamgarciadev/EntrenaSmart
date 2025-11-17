/**
 * Skeleton - Componente de carga placeholder animado
 *
 * Muestra placeholders animados mientras se cargan los datos reales.
 * Mejora la experiencia del usuario indicando que el contenido está cargando.
 */

interface SkeletonProps extends React.HTMLAttributes<HTMLDivElement> {
  /**
   * Ancho del skeleton (CSS value: "100%", "200px", etc.)
   */
  width?: string
  /**
   * Alto del skeleton (CSS value: "20px", "100%", etc.)
   */
  height?: string
  /**
   * Variante del skeleton
   */
  variant?: 'text' | 'circular' | 'rectangular'
}

export function Skeleton({
  className = '',
  width,
  height,
  variant = 'rectangular',
  ...props
}: SkeletonProps) {
  const variantClasses = {
    rectangular: 'rounded-md',
    circular: 'rounded-full',
    text: 'rounded',
  }

  return (
    <div
      className={`animate-pulse bg-gray-200 ${variantClasses[variant]} ${className}`}
      style={{
        width: width || '100%',
        height: height || (variant === 'text' ? '1rem' : '100%'),
      }}
      {...props}
    />
  )
}

/**
 * TableSkeleton - Skeleton específico para tablas
 */
interface TableSkeletonProps {
  rows?: number
  columns?: number
}

export function TableSkeleton({ rows = 5, columns = 4 }: TableSkeletonProps) {
  return (
    <div className="space-y-3">
      {/* Header */}
      <div className="flex gap-4 pb-2 border-b">
        {Array.from({ length: columns }).map((_, i) => (
          <Skeleton key={`header-${i}`} variant="text" width="100px" height="16px" />
        ))}
      </div>

      {/* Rows */}
      {Array.from({ length: rows }).map((_, rowIndex) => (
        <div key={`row-${rowIndex}`} className="flex gap-4 items-center">
          {Array.from({ length: columns }).map((_, colIndex) => (
            <Skeleton
              key={`cell-${rowIndex}-${colIndex}`}
              variant="text"
              width={colIndex === 0 ? '150px' : '100px'}
              height="14px"
            />
          ))}
        </div>
      ))}
    </div>
  )
}

/**
 * CardSkeleton - Skeleton específico para tarjetas
 */
export function CardSkeleton() {
  return (
    <div className="border rounded-lg p-6 space-y-4">
      <Skeleton variant="text" width="60%" height="24px" />
      <div className="space-y-2">
        <Skeleton variant="text" width="100%" height="16px" />
        <Skeleton variant="text" width="80%" height="16px" />
        <Skeleton variant="text" width="90%" height="16px" />
      </div>
      <div className="flex gap-2 pt-2">
        <Skeleton variant="rectangular" width="80px" height="36px" />
        <Skeleton variant="rectangular" width="80px" height="36px" />
      </div>
    </div>
  )
}

/**
 * FormSkeleton - Skeleton específico para formularios
 */
export function FormSkeleton() {
  return (
    <div className="space-y-4">
      {Array.from({ length: 3 }).map((_, i) => (
        <div key={`field-${i}`} className="space-y-2">
          <Skeleton variant="text" width="100px" height="14px" />
          <Skeleton variant="rectangular" width="100%" height="40px" />
        </div>
      ))}
      <div className="flex gap-2 pt-2">
        <Skeleton variant="rectangular" width="100px" height="40px" />
        <Skeleton variant="rectangular" width="100px" height="40px" />
      </div>
    </div>
  )
}
