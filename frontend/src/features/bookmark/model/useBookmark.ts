import { useMutation, useQueryClient } from '@tanstack/react-query'
import { bookmarkArticle, unbookmarkArticle } from '@/entities/article/api/articleApi'

export const useToggleBookmark = (articleId: number) => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (isBookmarked: boolean) =>
      isBookmarked ? unbookmarkArticle(articleId) : bookmarkArticle(articleId),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['article', articleId] })
      void queryClient.invalidateQueries({ queryKey: ['bookmarks'] })
    },
  })
}
