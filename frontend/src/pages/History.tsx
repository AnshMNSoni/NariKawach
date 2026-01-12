import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Shield, Clock, CheckCircle, AlertTriangle, Eye, Calendar, ChevronRight } from "lucide-react";
import BottomNav from "@/components/BottomNav";
import { format } from "date-fns";
import { getUser } from "@/utils/auth";

type Trip = {
  id: string;
  started_at: string;
  ended_at: string | null;
  status: "active" | "completed" | "emergency";
  end_risk_level: "low" | "medium" | "high" | null;
  notes: string | null;
};

const History = () => {
  const [trips, setTrips] = useState<Trip[]>([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const user = getUser();
    if (!user) {
      navigate("/auth");
      return;
    }
    fetchTrips(user.id);
  }, [navigate]);

  const fetchTrips = async (userId: string) => {
    try {
      const res = await fetch(`http://localhost:5000/trip/history/${userId}`);
      const data = await res.json();
      if (res.ok) {
        setTrips(data as Trip[]);
      }
    } catch (error) {
      console.error("Error fetching trips");
    } finally {
      setLoading(false);
    }
  };

  const getStatusIcon = (status: string, riskLevel: string | null) => {
    if (status === "emergency") {
      return <AlertTriangle className="w-5 h-5 text-emergency" />;
    }
    if (riskLevel === "medium") {
      return <Eye className="w-5 h-5 text-monitoring" />;
    }
    return <CheckCircle className="w-5 h-5 text-safe" />;
  };

  const getStatusLabel = (status: string, riskLevel: string | null) => {
    if (status === "emergency") return "Emergency";
    if (status === "active") return "In Progress";
    if (riskLevel === "medium") return "Completed (Alert)";
    return "Completed Safely";
  };

  const getStatusColor = (status: string, riskLevel: string | null) => {
    if (status === "emergency") return "bg-emergency/10 text-emergency border-emergency/20";
    if (riskLevel === "medium") return "bg-monitoring/10 text-monitoring border-monitoring/20";
    return "bg-safe/10 text-safe border-safe/20";
  };

  const formatDuration = (started: string, ended: string | null) => {
    if (!ended) return "Ongoing";
    const start = new Date(started);
    const end = new Date(ended);
    const mins = Math.round((end.getTime() - start.getTime()) / 60000);
    if (mins < 60) return `${mins} min`;
    const hours = Math.floor(mins / 60);
    const remainingMins = mins % 60;
    return `${hours}h ${remainingMins}m`;
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
          <span className="text-xl font-semibold text-foreground">Trip History</span>
        </div>
      </nav>

      {/* Content */}
      <div className="flex-1 container mx-auto px-4 py-6">
        <div className="max-w-lg mx-auto space-y-4">
          {trips.length === 0 ? (
            <div className="bg-card rounded-2xl shadow-soft border border-border/50 p-8 text-center animate-fade-in">
              <div className="w-14 h-14 rounded-2xl bg-muted flex items-center justify-center mx-auto mb-4">
                <Clock className="w-7 h-7 text-muted-foreground" />
              </div>
              <h3 className="text-lg font-semibold text-foreground mb-2">No Trips Yet</h3>
              <p className="text-sm text-muted-foreground">
                Your trip history will appear here once you start your first trip.
              </p>
            </div>
          ) : (
            trips.map((trip, index) => (
              <div
                key={trip.id}
                className="bg-card rounded-2xl shadow-soft border border-border/50 p-5 animate-fade-in"
                style={{ animationDelay: `${index * 0.05}s` }}
              >
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center gap-3">
                    {getStatusIcon(trip.status, trip.end_risk_level)}
                    <div>
                      <p className="font-medium text-foreground">
                        {format(new Date(trip.started_at), "MMM d, yyyy")}
                      </p>
                      <p className="text-xs text-muted-foreground">
                        {format(new Date(trip.started_at), "h:mm a")}
                      </p>
                    </div>
                  </div>
                  <span
                    className={`px-3 py-1 rounded-full text-xs font-medium border ${getStatusColor(
                      trip.status,
                      trip.end_risk_level
                    )}`}
                  >
                    {getStatusLabel(trip.status, trip.end_risk_level)}
                  </span>
                </div>

                <div className="flex items-center gap-4 text-sm text-muted-foreground">
                  <div className="flex items-center gap-1">
                    <Clock className="w-4 h-4" />
                    <span>{formatDuration(trip.started_at, trip.ended_at)}</span>
                  </div>
                  {trip.ended_at && (
                    <div className="flex items-center gap-1">
                      <Calendar className="w-4 h-4" />
                      <span>Ended {format(new Date(trip.ended_at), "h:mm a")}</span>
                    </div>
                  )}
                </div>

                {trip.notes && (
                  <p className="mt-3 text-sm text-muted-foreground border-t border-border/30 pt-3">
                    {trip.notes}
                  </p>
                )}
              </div>
            ))
          )}
        </div>
      </div>

      <BottomNav />
    </div>
  );
};

export default History;
