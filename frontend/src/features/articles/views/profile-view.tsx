import { observer } from 'mobx-react-lite';
import { User } from 'lucide-react';

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/common/components/ui/card';
import { Label } from '@/common/components/ui/label';
import { Separator } from '@/common/components/ui/separator';
import { authStore } from '@/features/auth/stores/auth-store';

export const ProfileView = observer(() => {
  if (!authStore.user) {
    return (
      <Card>
        <CardContent className="py-12 text-center text-muted-foreground">
          Please log in to view your profile.
        </CardContent>
      </Card>
    );
  }

  const user = authStore.user;

  return (
    <div className="mx-auto max-w-2xl space-y-8">
      <div className="space-y-1 border-b border-border pb-6">
        <h1 className="flex items-center gap-2 text-3xl font-bold tracking-tight">
          <User className="size-7 text-primary" />
          My profile
        </h1>
        <p className="text-muted-foreground">Your account details</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Account information</CardTitle>
          <CardDescription>Personal details linked to your account</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="space-y-1">
            <Label className="text-muted-foreground">Name</Label>
            <p className="text-lg font-medium">
              {user.first_name} {user.last_name}
            </p>
          </div>
          <Separator />
          <div className="space-y-1">
            <Label className="text-muted-foreground">Email</Label>
            <p className="text-lg font-medium">{user.email}</p>
          </div>
          <Separator />
          <div className="space-y-1">
            <Label className="text-muted-foreground">User ID</Label>
            <p className="font-mono text-sm text-muted-foreground">{user.id}</p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
});

ProfileView.displayName = 'ProfileView';
