import { z } from 'zod'

/**
 * Schema de validación para estudiante con Zod
 */
export const studentSchema = z.object({
  name: z.string()
    .min(2, 'El nombre debe tener al menos 2 caracteres')
    .max(100, 'El nombre no puede exceder 100 caracteres')
    .regex(
      /^[a-zA-ZáéíóúñÁÉÍÓÚÑ\s]+$/,
      'El nombre solo puede contener letras y espacios'
    ),
  
  telegram_username: z.string()
    .max(50, 'El username no puede exceder 50 caracteres')
    .regex(
      /^@?[a-zA-Z0-9_]*$/,
      'Username inválido. Solo letras, números y guiones bajos'
    )
    .optional()
    .or(z.literal('')),
  
  is_active: z.boolean().default(true),
})

export type StudentFormData = z.infer<typeof studentSchema>
