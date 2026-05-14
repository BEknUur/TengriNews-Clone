import { useQuery } from '@tanstack/react-query'
import { getTags } from '../api/tagApi'

export const useTags = () =>
  useQuery({
    queryKey: ['tags'],
    queryFn: getTags,
  })
