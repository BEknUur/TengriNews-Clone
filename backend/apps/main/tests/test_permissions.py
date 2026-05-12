from types import SimpleNamespace

from django.test import TestCase

from apps.main.permissions import (
	IsAdminOnly,
	IsAuthorOrEditorOrAdmin,
	IsCommentAuthorOrAdmin,
	IsEditorOrAdmin,
	IsOwnerOrAdmin,
)


class PermissionClassesTestCase(TestCase):
	def make_user(
		self,
		user_id: int,
		role: str | None = None,
		is_superuser: bool = False,
		is_authenticated: bool = True,
	) -> SimpleNamespace:
		return SimpleNamespace(
			id=user_id,
			role=role,
			is_superuser=is_superuser,
			is_authenticated=is_authenticated,
		)

	def make_request(self, user: SimpleNamespace) -> SimpleNamespace:
		return SimpleNamespace(user=user)

	def test_is_editor_or_admin_allows_editor(self) -> None:
		permission = IsEditorOrAdmin()
		request = self.make_request(self.make_user(user_id=1, role="EDITOR"))

		self.assertTrue(permission.has_permission(request=request, view=None))

	def test_is_editor_or_admin_denies_regular_user(self) -> None:
		permission = IsEditorOrAdmin()
		request = self.make_request(self.make_user(user_id=1, role="USER"))

		self.assertFalse(permission.has_permission(request=request, view=None))

	def test_is_admin_only_allows_superuser_without_role(self) -> None:
		permission = IsAdminOnly()
		request = self.make_request(
			self.make_user(user_id=1, role=None, is_superuser=True)
		)

		self.assertTrue(permission.has_permission(request=request, view=None))

	def test_is_author_or_editor_or_admin_allows_author(self) -> None:
		permission = IsAuthorOrEditorOrAdmin()
		request = self.make_request(self.make_user(user_id=10, role="USER"))
		article = SimpleNamespace(author_id=10)

		self.assertTrue(
			permission.has_object_permission(request=request, view=None, obj=article)
		)

	def test_is_author_or_editor_or_admin_denies_not_author_user(self) -> None:
		permission = IsAuthorOrEditorOrAdmin()
		request = self.make_request(self.make_user(user_id=10, role="USER"))
		article = SimpleNamespace(author_id=11)

		self.assertFalse(
			permission.has_object_permission(request=request, view=None, obj=article)
		)

	def test_is_comment_author_or_admin_allows_comment_author(self) -> None:
		permission = IsCommentAuthorOrAdmin()
		request = self.make_request(self.make_user(user_id=21, role="USER"))
		comment = SimpleNamespace(user_id=21)

		self.assertTrue(
			permission.has_object_permission(request=request, view=None, obj=comment)
		)

	def test_is_owner_or_admin_allows_profile_owner(self) -> None:
		permission = IsOwnerOrAdmin()
		request = self.make_request(self.make_user(user_id=7, role="USER"))
		profile_owner = SimpleNamespace(id=7)

		self.assertTrue(
			permission.has_object_permission(
				request=request,
				view=None,
				obj=profile_owner,
			)
		)

	def test_is_owner_or_admin_denies_non_owner_user(self) -> None:
		permission = IsOwnerOrAdmin()
		request = self.make_request(self.make_user(user_id=7, role="USER"))
		profile_owner = SimpleNamespace(id=9)

		self.assertFalse(
			permission.has_object_permission(
				request=request,
				view=None,
				obj=profile_owner,
			)
		)
