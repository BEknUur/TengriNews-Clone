import { useMutation, useQueryClient } from '@tanstack/react-query'
import { reactToArticle } from '@/entities/article/api/articleApi'

export const useReactToArticle = (articleId: number) => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (type: 'like' | 'dislike' | 'love' | 'laugh') =>
      reactToArticle(articleId, type),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['article', articleId] })
    },
  })
}
