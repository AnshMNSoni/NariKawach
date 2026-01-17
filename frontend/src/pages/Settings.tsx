import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import {
  Shield,
  User,
  Plus,
  LogOut,
  Lock,
  MapPin,
  Bell,
  ChevronRight,
  Zap
} from "lucide-react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { Badge } from "@/components/ui/badge";
import BottomNav from "@/components/BottomNav";
import ConfirmDialog from "@/components/ConfirmDialog";
import { useToast } from "@/hooks/use-toast";
import { z } from "zod";
import { getUser } from "@/utils/auth";
import { api } from "@/lib/api";

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
  const [logoutDialogOpen, setLogoutDialogOpen] = useState(false);

  const navigate = useNavigate();
  const { toast } = useToast();

  useEffect(() => {
    const user = getUser();
    if (!user) {
      navigate("/auth");
      return;
    }
    fetchGuardians(user.id);
  }, [navigate]);

  const fetchGuardians = async (userId: string) => {
    try {
      const { data } = await api.get(`/guardian/${userId}`);
      setGuardians(data);
    } catch (error) {
      console.error("Error fetching guardians", error);
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

    const user = getUser();
    if (!user) return;

    setSaving(true);
    try {
      const { data } = await api.post("/guardian/add", {
        user_id: user.id,
        name: name.trim(),
        phone: phone.trim(),
      });

      setGuardians([...guardians, data]);
      setName("");
      setPhone("");
      setShowAddForm(false);

      toast({
        title: "Guardian Added",
        description: `${data.name} has been added as a guardian.`,
      });
    } catch {
      toast({
        title: "Error",
        description: "Failed to add guardian.",
        variant: "destructive",
      });
    } finally {
      setSaving(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("nk_user");
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
          <span className="text-xl font-semibold">Settings</span>
        </div>
      </nav>

      {/* Content */}
      <div className="flex-1 container mx-auto px-4 py-4">
        <div className="max-w-lg mx-auto space-y-6">

          {/* Guardians */}
          <section className="bg-card rounded-2xl p-5 border shadow-soft">
            <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <User className="w-5 h-5 text-primary" />
              Guardians
            </h2>

            <div className="space-y-3">
              {guardians.map((g) => (
                <div
                  key={g.id}
                  className="flex items-center gap-3 p-3 bg-muted/30 rounded-xl"
                >
                  <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center">
                    <User className="w-5 h-5 text-primary" />
                  </div>
                  <div>
                    <p className="font-medium">{g.name}</p>
                    <p className="text-sm text-muted-foreground">{g.phone}</p>
                  </div>
                </div>
              ))}

              {showAddForm ? (
                <div className="space-y-3 p-4 bg-muted/30 rounded-xl">
                  <div>
                    <Label>Name</Label>
                    <Input value={name} onChange={(e) => setName(e.target.value)} />
                  </div>
                  <div>
                    <Label>Phone</Label>
                    <Input value={phone} onChange={(e) => setPhone(e.target.value)} />
                  </div>
                  <div className="flex gap-2">
                    <Button onClick={handleAddGuardian} disabled={saving}>
                      {saving ? "Adding..." : "Add Guardian"}
                    </Button>
                    <Button variant="outline" onClick={() => setShowAddForm(false)}>
                      Cancel
                    </Button>
                  </div>
                </div>
              ) : (
                <Button variant="outline" onClick={() => setShowAddForm(true)}>
                  <Plus className="w-4 h-4 mr-2" />
                  Add Guardian
                </Button>
              )}
            </div>
          </section>

          {/* Safety Controls */}
          <section className="bg-card rounded-2xl p-5 border shadow-soft">
            <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <Bell className="w-5 h-5 text-primary" />
              Safety Controls
            </h2>

            <div className="space-y-4">
              <div className="flex justify-between items-center p-3 bg-muted/30 rounded-xl">
                <p>Safety Monitoring</p>
                <Switch checked={safetyMonitoring} onCheckedChange={setSafetyMonitoring} />
              </div>
              <div className="flex justify-between items-center p-3 bg-muted/30 rounded-xl">
                <p>Emergency Escalation</p>
                <Switch checked={emergencyEscalation} onCheckedChange={setEmergencyEscalation} />
              </div>
            </div>
          </section>

          {/* Demo */}
          <button
            onClick={() => navigate("/home?demo=true")}
            className="w-full bg-card p-5 rounded-2xl border flex justify-between items-center"
          >
            <div className="flex items-center gap-3">
              <Zap className="w-5 h-5 text-primary" />
              <span>Demo Mode</span>
              <Badge variant="outline">Testing</Badge>
            </div>
            <ChevronRight />
          </button>

          {/* Logout */}
          <Button
            variant="outline"
            className="w-full text-destructive border-destructive/30"
            onClick={() => setLogoutDialogOpen(true)}
          >
            <LogOut className="w-5 h-5 mr-2" />
            Logout
          </Button>
        </div>
      </div>

      <BottomNav />

      <ConfirmDialog
        open={logoutDialogOpen}
        onOpenChange={setLogoutDialogOpen}
        title="Logout"
        description="Are you sure you want to logout?"
        confirmText="Logout"
        onConfirm={handleLogout}
        variant="destructive"
      />
    </div>
  );
};

export default Settings;
