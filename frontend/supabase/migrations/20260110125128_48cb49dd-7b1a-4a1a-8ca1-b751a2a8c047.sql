-- Create guardians table for emergency contacts
CREATE TABLE public.guardians (
  id UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  phone TEXT NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

-- Create risk_status table for monitoring safety status
CREATE TABLE public.risk_status (
  id UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE UNIQUE,
  risk_level TEXT NOT NULL DEFAULT 'low' CHECK (risk_level IN ('low', 'medium', 'high')),
  reason TEXT,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

-- Enable RLS on both tables
ALTER TABLE public.guardians ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.risk_status ENABLE ROW LEVEL SECURITY;

-- Guardians RLS policies
CREATE POLICY "Users can view their own guardians"
ON public.guardians FOR SELECT
USING (auth.uid() = user_id);

CREATE POLICY "Users can create their own guardians"
ON public.guardians FOR INSERT
WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own guardians"
ON public.guardians FOR UPDATE
USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own guardians"
ON public.guardians FOR DELETE
USING (auth.uid() = user_id);

-- Risk status RLS policies
CREATE POLICY "Users can view their own risk status"
ON public.risk_status FOR SELECT
USING (auth.uid() = user_id);

CREATE POLICY "Users can create their own risk status"
ON public.risk_status FOR INSERT
WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own risk status"
ON public.risk_status FOR UPDATE
USING (auth.uid() = user_id);

-- Create function to update timestamps
CREATE OR REPLACE FUNCTION public.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SET search_path = public;

-- Create triggers for automatic timestamp updates
CREATE TRIGGER update_guardians_updated_at
BEFORE UPDATE ON public.guardians
FOR EACH ROW
EXECUTE FUNCTION public.update_updated_at_column();

CREATE TRIGGER update_risk_status_updated_at
BEFORE UPDATE ON public.risk_status
FOR EACH ROW
EXECUTE FUNCTION public.update_updated_at_column();