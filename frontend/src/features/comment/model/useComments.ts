import { useMutation, useQueryClient } from '@tanstack/react-query'
import { addComment } from '@/entities/article/api/articleApi'

export const useAddComment = (articleId: number) => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ content, parent }: { content: string; parent?: number }) =>
      addComment(articleId, content, parent),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['article', articleId] })
    },
  })
}
