-- ============================================
-- SMART OFFICE OS - COMPLETE DATABASE SCHEMA
-- Multi-Tenant SaaS with Full Feature Set
-- ============================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================
-- 1. COMPANIES (Multi-Tenant Support)
-- ============================================
CREATE TABLE companies (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name VARCHAR(255) NOT NULL,
  slug VARCHAR(100) UNIQUE NOT NULL,
  email VARCHAR(255),
  phone VARCHAR(50),
  address TEXT,
  subscription_tier VARCHAR(50) DEFAULT 'free',
  subscription_status VARCHAR(50) DEFAULT 'active',
  monthly_task_limit INTEGER DEFAULT 100,
  settings JSONB DEFAULT '{}',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_companies_subscription ON companies(subscription_tier, subscription_status);

-- ============================================
-- 2. USERS WITH RBAC
-- ============================================
CREATE TYPE user_role AS ENUM ('super_admin', 'admin', 'manager', 'employee', 'client');

CREATE TABLE users (
  id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  email VARCHAR(255) UNIQUE NOT NULL,
  name VARCHAR(255) NOT NULL,
  role user_role DEFAULT 'employee',
  company_id UUID REFERENCES companies(id) ON DELETE SET NULL,
  avatar_url TEXT,
  phone VARCHAR(50),
  timezone VARCHAR(50) DEFAULT 'UTC',
  language VARCHAR(10) DEFAULT 'en',
  two_factor_enabled BOOLEAN DEFAULT FALSE,
  two_factor_secret VARCHAR(255),
  last_login TIMESTAMP WITH TIME ZONE,
  is_active BOOLEAN DEFAULT TRUE,
  metadata JSONB DEFAULT '{}',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_users_company ON users(company_id);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_email ON users(email);

-- ============================================
-- 3. ROLE PERMISSIONS (RBAC)
-- ============================================
CREATE TYPE permission_type AS ENUM (
  'task:create', 'task:read', 'task:update', 'task:delete', 'task:assign',
  'employee:read', 'employee:create', 'employee:update', 'employee:delete',
  'client:read', 'client:create', 'client:update', 'client:delete',
  'finance:read', 'finance:update',
  'report:read', 'report:export',
  'integration:manage',
  'company:settings'
);

CREATE TABLE role_permissions (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  role user_role NOT NULL,
  permission permission_type NOT NULL,
  company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  UNIQUE(role, permission, company_id)
);

CREATE INDEX idx_role_permissions ON role_permissions(role, company_id);

-- ============================================
-- 4. TASKS (Geo-Tagged, Priority, Status)
-- ============================================
CREATE TYPE task_priority AS ENUM ('low', 'medium', 'high', 'critical');
CREATE TYPE task_status AS ENUM ('pending', 'in_progress', 'completed', 'verified', 'cancelled', 'overdue');

CREATE TABLE tasks (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  title VARCHAR(500) NOT NULL,
  description TEXT,
  task_type VARCHAR(100),
  assigned_to UUID REFERENCES users(id) ON DELETE SET NULL,
  created_by UUID REFERENCES users(id) ON DELETE SET NULL,
  company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,

  -- Geo-tagging
  location_lat DECIMAL(10, 8),
  location_lng DECIMAL(11, 8),
  location_address TEXT,
  location_radius INTEGER DEFAULT 100, -- meters for verification

  -- Scheduling
  deadline TIMESTAMP WITH TIME ZONE,
  estimated_duration INTEGER, -- minutes
  actual_duration INTEGER,
  priority task_priority DEFAULT 'medium',
  status task_status DEFAULT 'pending',

  -- Payment
  payment_amount DECIMAL(10, 2) DEFAULT 0,
  payment_status VARCHAR(50) DEFAULT 'pending',

  -- AI/ML fields
  ai_suggested_priority task_priority,
  ai_risk_score DECIMAL(3, 2),
  ai_predicted_delay_days INTEGER,
  ai_notes TEXT,

  -- Tracking
  completion_notes TEXT,
  completed_at TIMESTAMP WITH TIME ZONE,
  verified_at TIMESTAMP WITH TIME ZONE,
  verification_photo_url TEXT,

  -- Smart routing
  required_skills JSONB DEFAULT '[]',
  workload_balance_score INTEGER DEFAULT 0,

  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_tasks_company ON tasks(company_id);
CREATE INDEX idx_tasks_assigned ON tasks(assigned_to);
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_deadline ON tasks(deadline);
CREATE INDEX idx_tasks_priority ON tasks(priority);
CREATE INDEX idx_tasks_created ON tasks(created_at);

-- ============================================
-- 5. ATTENDANCE (Geo-Verified Check-in)
-- ============================================
CREATE TABLE attendance (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,

  -- Location
  checkin_lat DECIMAL(10, 8) NOT NULL,
  checkin_lng DECIMAL(11, 8) NOT NULL,
  checkout_lat DECIMAL(10, 8),
  checkout_lng DECIMAL(11, 8),

  -- Timestamps
  checkin_time TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  checkout_time TIMESTAMP WITH TIME ZONE,

  -- Verification
  checkin_photo_url TEXT,
  checkin_verified BOOLEAN DEFAULT FALSE,
  verified_by UUID REFERENCES users(id),

  -- Task linkage
  linked_task_id UUID REFERENCES tasks(id),

  -- Work hours
  work_duration_minutes INTEGER,

  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_attendance_user ON attendance(user_id);
CREATE INDEX idx_attendance_company ON attendance(company_id);
CREATE INDEX idx_attendance_checkin ON attendance(checkin_time);
CREATE INDEX idx_attendance_linked_task ON attendance(linked_task_id);

-- ============================================
-- 6. PAYMENTS (Integrated Payouts)
-- ============================================
CREATE TYPE payment_status AS ENUM ('pending', 'processing', 'completed', 'failed', 'refunded');

CREATE TABLE payments (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  task_id UUID NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
  employee_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,

  amount DECIMAL(10, 2) NOT NULL,
  currency VARCHAR(3) DEFAULT 'INR',
  status payment_status DEFAULT 'pending',

  -- Payment gateway integration (generic)
  gateway_order_id VARCHAR(255),
  gateway_payment_id VARCHAR(255),
  gateway_signature VARCHAR(500),

  -- Payment details
  payment_method VARCHAR(50),
  gateway_fee DECIMAL(10, 2) DEFAULT 0,
  net_amount DECIMAL(10, 2),

  -- Approval workflow
  approved_by UUID REFERENCES users(id),
  approved_at TIMESTAMP WITH TIME ZONE,
  approval_notes TEXT,

  -- Transfer
  transferred_to_bank BOOLEAN DEFAULT FALSE,
  transferred_at TIMESTAMP WITH TIME ZONE,

  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_payments_employee ON payments(employee_id);
CREATE INDEX idx_payments_task ON payments(task_id);
CREATE INDEX idx_payments_status ON payments(status);
CREATE INDEX idx_payments_company ON payments(company_id);

-- ============================================
-- 7. CLIENTS (CRM Module)
-- ============================================
CREATE TABLE clients (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
  name VARCHAR(255) NOT NULL,
  email VARCHAR(255),
  phone VARCHAR(50),
  address TEXT,
  gstin VARCHAR(50),
  pan VARCHAR(50),

  -- Additional info
  contact_person VARCHAR(255),
  notes TEXT,
  tags JSONB DEFAULT '[]',

  created_by UUID REFERENCES users(id),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_clients_company ON clients(company_id);
CREATE INDEX idx_clients_email ON clients(email);

-- ============================================
-- 8. INVOICES (Billing System)
-- ============================================
CREATE TYPE invoice_status AS ENUM ('draft', 'sent', 'paid', 'overdue', 'cancelled');

CREATE TABLE invoices (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  invoice_number VARCHAR(100) UNIQUE NOT NULL,
  company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
  client_id UUID NOT NULL REFERENCES clients(id) ON DELETE CASCADE,

  -- Line items
  items JSONB DEFAULT '[]', -- [{task_id, description, quantity, rate, amount}]

  -- Financials
  subtotal DECIMAL(10, 2) NOT NULL,
  tax_percent DECIMAL(5, 2) DEFAULT 0,
  tax_amount DECIMAL(10, 2) DEFAULT 0,
  total_amount DECIMAL(10, 2) NOT NULL,
  currency VARCHAR(3) DEFAULT 'INR',

  -- Dates
  issue_date DATE NOT NULL,
  due_date DATE NOT NULL,
  paid_at TIMESTAMP WITH TIME ZONE,

  status invoice_status DEFAULT 'draft',

  -- External Invoice Reference
  external_invoice_id VARCHAR(255),
  payment_link_url TEXT,
  payment_link_id VARCHAR(255),

  notes TEXT,
  terms TEXT,

  created_by UUID REFERENCES users(id),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_invoices_company ON invoices(company_id);
CREATE INDEX idx_invoices_client ON invoices(client_id);
CREATE INDEX idx_invoices_status ON invoices(status);
CREATE INDEX idx_invoices_number ON invoices(invoice_number);

-- ============================================
-- 9. EXPENSES (Finance Module)
-- ============================================
CREATE TYPE expense_status AS ENUM ('pending', 'approved', 'rejected', 'reimbursed');

CREATE TABLE expenses (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
  submitted_by UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

  category VARCHAR(100) NOT NULL,
  amount DECIMAL(10, 2) NOT NULL,
  currency VARCHAR(3) DEFAULT 'INR',
  description TEXT,
  receipt_url TEXT,

  status expense_status DEFAULT 'pending',
  approved_by UUID REFERENCES users(id),
  approved_at TIMESTAMP WITH TIME ZONE,
  rejection_reason TEXT,

  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_expenses_company ON expenses(company_id);
CREATE INDEX idx_expenses_submitted ON expenses(submitted_by);
CREATE INDEX idx_expenses_status ON expenses(status);

-- ============================================
-- 10. LEAVE REQUESTS (HR Module)
-- ============================================
CREATE TYPE leave_type AS ENUM ('sick', 'casual', 'earned', 'maternity', 'paternity', 'unpaid');
CREATE TYPE leave_status AS ENUM ('pending', 'approved', 'rejected', 'cancelled');

CREATE TABLE leave_requests (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,

  leave_type leave_type NOT NULL,
  start_date DATE NOT NULL,
  end_date DATE NOT NULL,
  total_days INTEGER NOT NULL,
  reason TEXT,
  status leave_status DEFAULT 'pending',

  approved_by UUID REFERENCES users(id),
  approved_at TIMESTAMP WITH TIME ZONE,
  rejection_reason TEXT,

  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_leave_requests_user ON leave_requests(user_id);
CREATE INDEX idx_leave_requests_company ON leave_requests(company_id);
CREATE INDEX idx_leave_requests_status ON leave_requests(status);

-- ============================================
-- 11. AI LOGS (For Analytics & Training)
-- ============================================
CREATE TYPE ai_action_type AS ENUM ('parse_task', 'summarize', 'extract', 'predict_risk', 'suggest_deadline', 'recommend_assignee');

CREATE TABLE ai_logs (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  company_id UUID REFERENCES companies(id) ON DELETE SET NULL,
  user_id UUID REFERENCES users(id) ON DELETE SET NULL,

  action ai_action_type NOT NULL,
  input_text TEXT NOT NULL,
  output_data JSONB NOT NULL,
  confidence_score DECIMAL(3, 2),

  -- Feedback loop
  user_feedback BOOLEAN,
  corrected_data JSONB,

  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_ai_logs_company ON ai_logs(company_id);
CREATE INDEX idx_ai_logs_action ON ai_logs(action);
CREATE INDEX idx_ai_logs_created ON ai_logs(created_at);

-- ============================================
-- 12. PREDICTIONS (Analytics Engine)
-- ============================================
CREATE TABLE predictions (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  task_id UUID REFERENCES tasks(id) ON DELETE CASCADE,
  company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,

  -- Predictions
  delay_risk DECIMAL(3, 2) DEFAULT 0, -- 0-1 probability
  workload_score INTEGER DEFAULT 0, -- 0-100
  performance_score DECIMAL(3, 2),

  -- Insights
  suggested_deadline TIMESTAMP WITH TIME ZONE,
  risk_factors JSONB DEFAULT '[]',
  recommendation_text TEXT,

  -- History
  prediction_made_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  actual_outcome JSONB, -- Store actual results for model training

  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_predictions_task ON predictions(task_id);
CREATE INDEX idx_predictions_company ON predictions(company_id);
CREATE INDEX idx_predictions_risk ON predictions(delay_risk);

-- ============================================
-- 13. ACTIVITY LOGS (Audit Trail)
-- ============================================
CREATE TYPE activity_action AS ENUM (
  'login', 'logout', 'task_created', 'task_updated', 'task_completed',
  'payment_processed', 'user_invited', 'permission_changed',
  'checkin', 'checkout', 'geo_verification_failed'
);

CREATE TABLE activity_logs (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
  user_id UUID REFERENCES users(id) ON DELETE SET NULL,

  action activity_action NOT NULL,
  resource_type VARCHAR(50),
  resource_id UUID,
  changes JSONB,
  ip_address INET,
  user_agent TEXT,
  metadata JSONB DEFAULT '{}',

  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_activity_logs_company ON activity_logs(company_id);
CREATE INDEX idx_activity_logs_user ON activity_logs(user_id);
CREATE INDEX idx_activity_logs_created ON activity_logs(created_at);

-- ============================================
-- 14. INTEGRATIONS (Third-party Connections)
-- ============================================
CREATE TYPE integration_service AS ENUM ('slack', 'zoom', 'google_drive', 'github', 'microsoft_teams', 'zapier');

CREATE TABLE integrations (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,

  service integration_service NOT NULL,
  display_name VARCHAR(255),

  -- OAuth tokens (encrypted)
  access_token TEXT,
  refresh_token TEXT,
  token_expiry TIMESTAMP WITH TIME ZONE,

  -- Configuration
  config JSONB DEFAULT '{}',
  webhook_url TEXT,
  is_active BOOLEAN DEFAULT TRUE,

  created_by UUID REFERENCES users(id),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_integrations_company ON integrations(company_id);
CREATE INDEX idx_integrations_service ON integrations(service);

-- ============================================
-- 15. NOTIFICATIONS (Real-time)
-- ============================================
CREATE TYPE notification_type AS ENUM ('task_assigned', 'task_due_soon', 'task_overdue', 'payment_received',
                                       'approval_required', 'risk_alert', 'daily_summary', 'weekly_report');

CREATE TABLE notifications (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,

  type notification_type NOT NULL,
  title VARCHAR(500) NOT NULL,
  message TEXT,
  action_url TEXT,
  related_id UUID, -- task_id, payment_id, etc.

  -- Delivery
  is_read BOOLEAN DEFAULT FALSE,
  read_at TIMESTAMP WITH TIME ZONE,
  delivered_via JSONB DEFAULT '["in_app"]', -- ["in_app", "email", "push", "slack"]

  -- Expiry
  expires_at TIMESTAMP WITH TIME ZONE,

  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_notifications_user ON notifications(user_id);
CREATE INDEX idx_notifications_company ON notifications(company_id);
CREATE INDEX idx_notifications_unread ON notifications(is_read) WHERE is_read = FALSE;

-- ============================================
-- 16. DOCUMENTS (File Attachments)
-- ============================================
CREATE TABLE documents (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
  uploaded_by UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

  filename VARCHAR(500) NOT NULL,
  original_name VARCHAR(500) NOT NULL,
  file_size INTEGER NOT NULL,
  mime_type VARCHAR(100),
  storage_path TEXT NOT NULL,

  -- Association
  task_id UUID REFERENCES tasks(id) ON DELETE SET NULL,
  expense_id UUID REFERENCES expenses(id) ON DELETE SET NULL,

  -- AI extracted data
  ai_extracted_text TEXT,
  ai_summary TEXT,
  ai_keywords JSONB DEFAULT '[]',

  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_documents_company ON documents(company_id);
CREATE INDEX idx_documents_task ON documents(task_id);
CREATE INDEX idx_documents_uploaded ON documents(uploaded_by);

-- ============================================
-- 17. SETTINGS (Company Configuration)
-- ============================================
CREATE TABLE company_settings (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  company_id UUID UNIQUE NOT NULL REFERENCES companies(id) ON DELETE CASCADE,

  -- Email templates
  email_templates JSONB DEFAULT '{}',

  -- Notification preferences
  notification_prefs JSONB DEFAULT '{}',

  -- Working hours
  working_hours JSONB DEFAULT '{"start": "09:00", "end": "18:00", "timezone": "UTC"}',

  -- Geo verification settings
  geo_verification_radius INTEGER DEFAULT 100,

  -- Payment settings
  payment_currency VARCHAR(3) DEFAULT 'INR',
  payment_gateway JSONB DEFAULT '{}',

  -- AI settings
  ai_enabled BOOLEAN DEFAULT TRUE,
  ai_confidence_threshold DECIMAL(3, 2) DEFAULT 0.8,

  -- Integration configs
  integration_configs JSONB DEFAULT '{}',

  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_company_settings_company ON company_settings(company_id);

-- ============================================
-- 18. WEBHOOKS (Event-driven)
-- ============================================
CREATE TABLE webhooks (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,

  event_type VARCHAR(100) NOT NULL,
  target_url TEXT NOT NULL,
  secret_token VARCHAR(255),

  is_active BOOLEAN DEFAULT TRUE,
  last_triggered_at TIMESTAMP WITH TIME ZONE,
  failure_count INTEGER DEFAULT 0,

  created_by UUID REFERENCES users(id),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_webhooks_company ON webhooks(company_id);

-- ============================================
-- FUNCTIONS & TRIGGERS
-- ============================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply updated_at triggers to all relevant tables
CREATE TRIGGER update_companies_updated_at BEFORE UPDATE ON companies FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_tasks_updated_at BEFORE UPDATE ON tasks FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_payments_updated_at BEFORE UPDATE ON payments FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_clients_updated_at BEFORE UPDATE ON clients FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_invoices_updated_at BEFORE UPDATE ON invoices FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_expenses_updated_at BEFORE UPDATE ON expenses FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_leave_requests_updated_at BEFORE UPDATE ON leave_requests FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_integrations_updated_at BEFORE UPDATE ON integrations FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_company_settings_updated_at BEFORE UPDATE ON company_settings FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to auto-generate invoice numbers
CREATE OR REPLACE FUNCTION generate_invoice_number()
RETURNS TRIGGER AS $$
DECLARE
  year_val TEXT;
  month_val TEXT;
  seq_val INTEGER;
  prefix TEXT;
BEGIN
  year_val := EXTRACT(YEAR FROM CURRENT_DATE)::TEXT;
  month_val := LPAD(EXTRACT(MONTH FROM CURRENT_DATE)::TEXT, 2, '0');

  SELECT COALESCE(MAX(CAST(SPLIT_PART(invoice_number, '-', 3) AS INTEGER)), 0) + 1
  INTO seq_val
  FROM invoices
  WHERE invoice_number LIKE 'INV-' || year_val || '-' || month_val || '-%';

  NEW.invoice_number := 'INV-' || year_val || '-' || month_val || '-' || LPAD(seq_val::TEXT, 4, '0');
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER set_invoice_number BEFORE INSERT ON invoices FOR EACH ROW EXECUTE FUNCTION generate_invoice_number();

-- View for employee performance analytics
CREATE OR REPLACE VIEW employee_performance AS
SELECT
  u.id as employee_id,
  u.name,
  u.company_id,
  COUNT(t.id) as total_tasks_assigned,
  COUNT(t.id) FILTER (WHERE t.status = 'completed') as tasks_completed,
  COUNT(t.id) FILTER (WHERE t.status = 'overdue') as tasks_overdue,
  COALESCE(SUM(t.payment_amount) FILTER (WHERE t.status = 'completed'), 0) as total_earnings,
  AVG(EXTRACT(EPOCH FROM (t.completed_at - t.created_at))/3600) as avg_completion_hours,
  COUNT(p.id) as payments_received
FROM users u
LEFT JOIN tasks t ON u.id = t.assigned_to
LEFT JOIN payments p ON t.id = p.task_id AND p.status = 'completed'
WHERE u.role IN ('employee')
GROUP BY u.id, u.name, u.company_id;

-- View for daily attendance summary
CREATE OR REPLACE VIEW daily_attendance_summary AS
SELECT
  u.id as user_id,
  u.name,
  u.company_id,
  DATE(a.checkin_time) as date,
  MIN(a.checkin_time) as first_checkin,
  MAX(a.checkout_time) as last_checkout,
  COUNT(a.id) as total_checkins,
  SUM(a.work_duration_minutes) as total_work_minutes
FROM users u
LEFT JOIN attendance a ON u.id = a.user_id AND DATE(a.checkin_time) = CURRENT_DATE
WHERE u.company_id IS NOT NULL
GROUP BY u.id, u.name, u.company_id, DATE(a.checkin_time);

COMMENT ON TABLE companies IS 'Multi-tenant company data - each company is isolated';
COMMENT ON TABLE users IS 'User accounts with role-based access control';
COMMENT ON TABLE tasks IS 'Geo-tagged tasks with AI predictions and smart routing';
COMMENT ON TABLE attendance IS 'Location-verified check-in/out system';
COMMENT ON TABLE payments IS 'Payment processing system for tasks';
COMMENT ON TABLE ai_logs IS 'AI assistant interaction history for analytics';
COMMENT ON TABLE predictions IS 'Predictive analytics and risk scoring';