export type Role = 'user' | 'assistant'
export interface Message {
  id: string
  role: Role
  text: string
  pending?: boolean // true while streaming
  error?: boolean
}
