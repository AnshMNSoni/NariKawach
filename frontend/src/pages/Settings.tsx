import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Shield, User, Phone, Plus, Trash2, LogOut, Lock, MapPin, Bell, ChevronRight, Zap } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { useToast } from "@/hooks/use-toast";
import { supabase } from "@/integrations/supabase/client";
import BottomNav from "@/components/BottomNav";
import ConfirmDialog from "@/components/ConfirmDialog";
import { z } from "zod";
import { Badge } from "@/components/ui/badge";

type Guardian = {
  id: string;
  name: string;
  phone: string;
};

const guardianSchema = z.object({
  name: z.string().trim().min(1, "Name is required").max(100),
  phone: z.string().trim().min(10, "Valid phone required").max(20),
});

const Settings = () => {
  const [guardians, setGuardians] = useState<Guardian[]>([]);
  const [showAddForm, setShowAddForm] = useState(false);
  const [name, setName] = useState("");
  const [phone, setPhone] = useState("");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [safetyMonitoring, setSafetyMonitoring] = useState(true);
  const [emergencyEscalation, setEmergencyEscalation] = useState(true);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [guardianToDelete, setGuardianToDelete] = useState<string | null>(null);
  const [logoutDialogOpen, setLogoutDialogOpen] = useState(false);
  const navigate = useNavigate();
  const { toast } = useToast();

  useEffect(() => {
    const checkAuth = async () => {
      const { data: { session } } = await supabase.auth.getSession();
      if (!session?.user) {
        navigate("/auth");
        return;
      }
      fetchGuardians(session.user.id);
    };
    checkAuth();
  }, [navigate]);

  const fetchGuardians = async (userId: string) => {
    try {
      const { data } = await supabase
        .from("guardians")
        .select("id, name, phone")
        .eq("user_id", userId);

      if (data) {
        setGuardians(data);
      }
    } catch (error) {
      console.error("Error fetching guardians");
    } finally {
      setLoading(false);
    }
  };

  const handleAddGuardian = async () => {
    const validation = guardianSchema.safeParse({ name, phone });
    if (!validation.success) {
      toast({
        title: "Validation Error",
        description: validation.error.errors[0].message,
        variant: "destructive",
      });
      return;
    }

    const session = await supabase.auth.getSession();
    if (!session.data.session?.user) return;

    setSaving(true);
    try {
      const { data, error } = await supabase.from("guardians").insert({
        user_id: session.data.session.user.id,
        name: name.trim(),
        phone: phone.trim(),
      }).select().single();

      if (error) throw error;

      if (data) {
        setGuardians([...guardians, data]);
        setName("");
        setPhone("");
        setShowAddForm(false);
        toast({ title: "Guardian Added", description: `${data.name} has been added as a guardian.` });
      }
    } catch (error) {
      toast({ title: "Error", description: "Failed to add guardian.", variant: "destructive" });
    } finally {
      setSaving(false);
    }
  };

  const confirmDeleteGuardian = (id: string) => {
    setGuardianToDelete(id);
    setDeleteDialogOpen(true);
  };

  const handleDeleteGuardian = async () => {
    if (!guardianToDelete) return;

    try {
      await supabase.from("guardians").delete().eq("id", guardianToDelete);
      setGuardians(guardians.filter((g) => g.id !== guardianToDelete));
      toast({ title: "Guardian Removed" });
    } catch (error) {
      toast({ title: "Error", description: "Failed to remove guardian.", variant: "destructive" });
    } finally {
      setDeleteDialogOpen(false);
      setGuardianToDelete(null);
    }
  };

  const handleLogout = async () => {
    await supabase.auth.signOut();
    navigate("/auth");
  };

  if (loading) {
    return (
      <div className="min-h-screen gradient-hero flex items-center justify-center">
        <div className="w-8 h-8 border-2 border-primary/30 border-t-primary rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="min-h-screen gradient-hero flex flex-col pb-24">
      {/* Header */}
      <nav className="container mx-auto px-4 py-6">
        <div className="flex items-center gap-2">
          <div className="w-10 h-10 rounded-xl bg-primary/10 flex items-center justify-center">
            <Shield className="w-5 h-5 text-primary" />
          </div>
          <span className="text-xl font-semibold text-foreground">Settings</span>
        </div>
      </nav>

      {/* Content */}
      <div className="flex-1 container mx-auto px-4 py-4">
        <div className="max-w-lg mx-auto space-y-6">
          {/* Guardians Section */}
          <section className="bg-card rounded-2xl shadow-soft border border-border/50 p-5 animate-fade-in">
            <h2 className="text-lg font-semibold text-foreground mb-4 flex items-center gap-2">
              <User className="w-5 h-5 text-primary" />
              Guardians
            </h2>
            <p className="text-sm text-muted-foreground mb-4">
              Trusted contacts who will be notified in emergencies.
            </p>

            <div className="space-y-3">
              {guardians.map((guardian) => (
                <div
                  key={guardian.id}
                  className="flex items-center justify-between p-3 bg-muted/30 rounded-xl"
                >
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center">
                      <User className="w-5 h-5 text-primary" />
                    </div>
                    <div>
                      <p className="font-medium text-foreground">{guardian.name}</p>
                      <p className="text-sm text-muted-foreground">{guardian.phone}</p>
                    </div>
                  </div>
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => confirmDeleteGuardian(guardian.id)}
                    className="text-muted-foreground hover:text-destructive"
                  >
                    <Trash2 className="w-4 h-4" />
                  </Button>
                </div>
              ))}

              {showAddForm ? (
                <div className="space-y-3 p-4 bg-muted/30 rounded-xl">
                  <div className="space-y-2">
                    <Label htmlFor="guardian-name" className="text-sm">Name</Label>
                    <Input
                      id="guardian-name"
                      placeholder="Guardian name"
                      value={name}
                      onChange={(e) => setName(e.target.value)}
                      className="h-11"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="guardian-phone" className="text-sm">Phone</Label>
                    <Input
                      id="guardian-phone"
                      type="tel"
                      placeholder="+91 98765 43210"
                      value={phone}
                      onChange={(e) => setPhone(e.target.value)}
                      className="h-11"
                    />
                  </div>
                  <div className="flex gap-2">
                    <Button onClick={handleAddGuardian} disabled={saving} className="flex-1">
                      {saving ? "Adding..." : "Add Guardian"}
                    </Button>
                    <Button variant="outline" onClick={() => setShowAddForm(false)}>
                      Cancel
                    </Button>
                  </div>
                </div>
              ) : (
                <Button
                  variant="outline"
                  className="w-full"
                  onClick={() => setShowAddForm(true)}
                >
                  <Plus className="w-4 h-4 mr-2" />
                  Add Guardian
                </Button>
              )}
            </div>
          </section>

          {/* Safety Controls Section */}
          <section className="bg-card rounded-2xl shadow-soft border border-border/50 p-5 animate-fade-in">
            <h2 className="text-lg font-semibold text-foreground mb-4 flex items-center gap-2">
              <Bell className="w-5 h-5 text-primary" />
              Safety Controls
            </h2>

            <div className="space-y-4">
              <div className="flex items-center justify-between p-3 bg-muted/30 rounded-xl">
                <div>
                  <p className="font-medium text-foreground">Safety Monitoring</p>
                  <p className="text-sm text-muted-foreground">Track location during active trips</p>
                </div>
                <Switch checked={safetyMonitoring} onCheckedChange={setSafetyMonitoring} />
              </div>

              <div className="flex items-center justify-between p-3 bg-muted/30 rounded-xl">
                <div>
                  <p className="font-medium text-foreground">Emergency Escalation</p>
                  <p className="text-sm text-muted-foreground">Auto-notify guardians on high risk</p>
                </div>
                <Switch checked={emergencyEscalation} onCheckedChange={setEmergencyEscalation} />
              </div>
            </div>
          </section>

          {/* Privacy Section */}
          <section className="bg-card rounded-2xl shadow-soft border border-border/50 p-5 animate-fade-in">
            <h2 className="text-lg font-semibold text-foreground mb-4 flex items-center gap-2">
              <Lock className="w-5 h-5 text-primary" />
              Privacy
            </h2>

            <div className="flex gap-3 p-4 bg-muted/30 rounded-xl">
              <MapPin className="w-5 h-5 text-primary flex-shrink-0 mt-0.5" />
              <div>
                <p className="font-medium text-foreground mb-1">Location Data</p>
                <p className="text-sm text-muted-foreground">
                  Location data is only used during active trips and is never shared without your consent.
                </p>
              </div>
            </div>
          </section>

          {/* Preferences Link */}
          <button
            onClick={() => navigate("/preferences")}
            className="w-full bg-card rounded-2xl shadow-soft border border-border/50 p-5 flex items-center justify-between hover:bg-muted/30 transition-colors animate-fade-in"
          >
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-primary/10 flex items-center justify-center">
                <Bell className="w-5 h-5 text-primary" />
              </div>
              <div className="text-left">
                <p className="font-medium text-foreground">Safety Preferences</p>
                <p className="text-sm text-muted-foreground">Customize sensitivity & alerts</p>
              </div>
            </div>
            <ChevronRight className="w-5 h-5 text-muted-foreground" />
          </button>

          {/* Developer Options Section */}
          <section className="bg-card rounded-2xl shadow-soft border border-border/50 p-5 animate-fade-in">
            <h2 className="text-lg font-semibold text-foreground mb-4 flex items-center gap-2">
              <Zap className="w-5 h-5 text-primary" />
              Developer Options
            </h2>

            <button
              onClick={() => navigate("/home?demo=true")}
              className="w-full flex items-center justify-between p-3 bg-muted/30 rounded-xl hover:bg-muted/50 transition-colors"
            >
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-primary/10 flex items-center justify-center">
                  <Zap className="w-5 h-5 text-primary" />
                </div>
                <div className="text-left">
                  <div className="flex items-center gap-2">
                    <p className="font-medium text-foreground">Demo Mode</p>
                    <Badge variant="outline" className="text-xs">Testing</Badge>
                  </div>
                  <p className="text-sm text-muted-foreground">
                    Simulate risk escalation workflow
                  </p>
                </div>
              </div>
              <ChevronRight className="w-5 h-5 text-muted-foreground" />
            </button>
          </section>

          {/* Logout Button */}
          <Button
            variant="outline"
            className="w-full h-12 text-destructive border-destructive/30 hover:bg-destructive/10"
            onClick={() => setLogoutDialogOpen(true)}
          >
            <LogOut className="w-5 h-5 mr-2" />
            Logout
          </Button>
        </div>
      </div>

      <BottomNav />

      <ConfirmDialog
        open={deleteDialogOpen}
        onOpenChange={setDeleteDialogOpen}
        title="Remove Guardian"
        description="Are you sure you want to remove this guardian? They will no longer be notified in emergencies."
        confirmText="Remove"
        onConfirm={handleDeleteGuardian}
        variant="destructive"
      />

      <ConfirmDialog
        open={logoutDialogOpen}
        onOpenChange={setLogoutDialogOpen}
        title="Logout"
        description="Are you sure you want to logout? You'll need to sign in again to access your safety features."
        confirmText="Logout"
        onConfirm={handleLogout}
        variant="destructive"
      />
    </div>
  );
};

export default Settings;
