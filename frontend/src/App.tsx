import { useMemo, useState } from "react";
import {
  BarChart3,
  Database,
  FileText,
  RefreshCw,
  Save,
  TrendingUp,
} from "lucide-react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

const API_BASE = "http://127.0.0.1:8000";

type DreAccountLine = {
  account_code: string;
  account_name: string;
  amount: number;
};

type DreGroupLine = {
  group: string;
  amount: number;
  accounts: DreAccountLine[];
};

type DreResponse = {
  source_file_id: string;
  summary: {
    total_revenue: number;
    total_expenses: number;
    net_result: number;
  };
  groups: DreGroupLine[];
};

type TrialBalanceLine = {
  account_code: string;
  account_name: string;
  total_debit: number;
  total_credit: number;
};

type TrialBalanceResponse = {
  source_file_id: string;
  lines: TrialBalanceLine[];
};

type SaveDreResponse = {
  report_id: string;
  source_file_id: string;
  report_type: string;
  message: string;
};

const money = (value: number) =>
  new Intl.NumberFormat("pt-BR", {
    style: "currency",
    currency: "BRL",
  }).format(value ?? 0);

const cardStyle: React.CSSProperties = {
  background: "#fff",
  borderRadius: 20,
  border: "1px solid #e5e7eb",
  boxShadow: "0 6px 20px rgba(15, 23, 42, 0.05)",
};

const sectionTitleStyle: React.CSSProperties = {
  fontSize: 18,
  fontWeight: 700,
  margin: 0,
};

export default function App() {
  const [sourceFileId, setSourceFileId] = useState(
    "93522783-4b21-4c0d-bfc3-1df07b6d06fb"
  );
  const [dre, setDre] = useState<DreResponse | null>(null);
  const [trialBalance, setTrialBalance] = useState<TrialBalanceResponse | null>(
    null
  );
  const [saveResult, setSaveResult] = useState<SaveDreResponse | null>(null);
  const [status, setStatus] = useState("");
  const [activeTab, setActiveTab] = useState<"dre" | "balancete" | "graficos">(
    "dre"
  );
  const [loadingDre, setLoadingDre] = useState(false);
  const [loadingTrial, setLoadingTrial] = useState(false);
  const [savingDre, setSavingDre] = useState(false);

  const barData = useMemo(() => {
    if (!dre) return [];
    return [
      { name: "Receitas", value: dre.summary.total_revenue },
      { name: "Despesas", value: dre.summary.total_expenses },
      { name: "Resultado", value: dre.summary.net_result },
    ];
  }, [dre]);

  const pieData = useMemo(() => {
    if (!dre) return [];
    return dre.groups.map((group) => ({
      name: group.group,
      value: group.amount,
    }));
  }, [dre]);

  async function fetchDre() {
    try {
      setLoadingDre(true);
      setStatus("Carregando DRE...");
      setSaveResult(null);

      const response = await fetch(`${API_BASE}/files/${sourceFileId}/dre`);
      if (!response.ok) {
        throw new Error(await response.text());
      }

      const data: DreResponse = await response.json();
      setDre(data);
      setStatus("DRE carregada com sucesso.");
    } catch (error) {
      setStatus(
        error instanceof Error ? error.message : "Erro ao carregar DRE."
      );
    } finally {
      setLoadingDre(false);
    }
  }

  async function fetchTrialBalance() {
    try {
      setLoadingTrial(true);
      setStatus("Carregando balancete...");

      const response = await fetch(
        `${API_BASE}/files/${sourceFileId}/trial-balance`
      );
      if (!response.ok) {
        throw new Error(await response.text());
      }

      const data: TrialBalanceResponse = await response.json();
      setTrialBalance(data);
      setStatus("Balancete carregado com sucesso.");
    } catch (error) {
      setStatus(
        error instanceof Error ? error.message : "Erro ao carregar balancete."
      );
    } finally {
      setLoadingTrial(false);
    }
  }

  async function saveDre() {
    try {
      setSavingDre(true);
      setStatus("Salvando DRE...");

      const response = await fetch(
        `${API_BASE}/files/${sourceFileId}/dre/save`,
        {
          method: "POST",
        }
      );
      if (!response.ok) {
        throw new Error(await response.text());
      }

      const data: SaveDreResponse = await response.json();
      setSaveResult(data);
      setStatus("DRE salva com sucesso.");
    } catch (error) {
      setStatus(
        error instanceof Error ? error.message : "Erro ao salvar DRE."
      );
    } finally {
      setSavingDre(false);
    }
  }

  return (
    <div
      style={{
        minHeight: "100vh",
        background: "#f8fafc",
        color: "#0f172a",
        fontFamily:
          "Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif",
      }}
    >
      <div
        style={{
          maxWidth: 1280,
          margin: "0 auto",
          padding: 24,
          display: "grid",
          gap: 24,
        }}
      >
        <div
          style={{
            ...cardStyle,
            padding: 24,
            display: "grid",
            gap: 18,
          }}
        >
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: 14,
              flexWrap: "wrap",
            }}
          >
            <div
              style={{
                width: 52,
                height: 52,
                borderRadius: 16,
                background: "#e2e8f0",
                display: "grid",
                placeItems: "center",
              }}
            >
              <TrendingUp size={24} />
            </div>

            <div>
              <h1
                style={{
                  margin: 0,
                  fontSize: 28,
                  fontWeight: 800,
                }}
              >
                Dashboard Contábil
              </h1>
              <p style={{ margin: "6px 0 0", color: "#475569" }}>
                Frontend inicial em React consumindo seu backend FastAPI.
              </p>
            </div>
          </div>

          <div
            style={{
              display: "grid",
              gridTemplateColumns: "1fr auto auto auto",
              gap: 12,
            }}
          >
            <input
              value={sourceFileId}
              onChange={(e) => setSourceFileId(e.target.value)}
              placeholder="Cole o source_file_id"
              style={{
                height: 46,
                borderRadius: 14,
                border: "1px solid #cbd5e1",
                padding: "0 14px",
                fontSize: 14,
                outline: "none",
              }}
            />

            <button
              onClick={fetchDre}
              disabled={loadingDre}
              style={buttonStyle("#0f172a")}
            >
              <RefreshCw size={16} />
              {loadingDre ? "Carregando..." : "Carregar DRE"}
            </button>

            <button
              onClick={fetchTrialBalance}
              disabled={loadingTrial}
              style={buttonStyle("#334155")}
            >
              <Database size={16} />
              {loadingTrial ? "Carregando..." : "Balancete"}
            </button>

            <button
              onClick={saveDre}
              disabled={savingDre}
              style={buttonStyle("#ffffff", "#0f172a")}
            >
              <Save size={16} />
              {savingDre ? "Salvando..." : "Salvar DRE"}
            </button>
          </div>

          <div
            style={{
              display: "flex",
              gap: 12,
              alignItems: "center",
              justifyContent: "space-between",
              flexWrap: "wrap",
              background: "#f8fafc",
              border: "1px solid #e2e8f0",
              borderRadius: 16,
              padding: "12px 16px",
            }}
          >
            <div>
              <div style={{ fontSize: 12, color: "#64748b" }}>Status</div>
              <div style={{ fontWeight: 600 }}>{status || "Aguardando ação"}</div>
            </div>

            <div>
              <div style={{ fontSize: 12, color: "#64748b" }}>API</div>
              <div style={{ fontWeight: 600 }}>{API_BASE}</div>
            </div>
          </div>

          {saveResult && (
            <div
              style={{
                background: "#ecfeff",
                border: "1px solid #a5f3fc",
                color: "#0f172a",
                borderRadius: 16,
                padding: 14,
              }}
            >
              <strong>DRE salva com sucesso.</strong>
              <div style={{ marginTop: 6, fontSize: 14 }}>
                Report ID: {saveResult.report_id}
              </div>
            </div>
          )}
        </div>

        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(3, minmax(0, 1fr))",
            gap: 16,
          }}
        >
          <MetricCard
            icon={<TrendingUp size={18} />}
            label="Receitas"
            value={money(dre?.summary.total_revenue ?? 0)}
          />
          <MetricCard
            icon={<FileText size={18} />}
            label="Despesas"
            value={money(dre?.summary.total_expenses ?? 0)}
          />
          <MetricCard
            icon={<BarChart3 size={18} />}
            label="Resultado"
            value={money(dre?.summary.net_result ?? 0)}
          />
        </div>

        <div style={{ ...cardStyle, padding: 16 }}>
          <div style={{ display: "flex", gap: 10, marginBottom: 18 }}>
            <TabButton
              active={activeTab === "dre"}
              onClick={() => setActiveTab("dre")}
              label="DRE"
            />
            <TabButton
              active={activeTab === "balancete"}
              onClick={() => setActiveTab("balancete")}
              label="Balancete"
            />
            <TabButton
              active={activeTab === "graficos"}
              onClick={() => setActiveTab("graficos")}
              label="Gráficos"
            />
          </div>

          {activeTab === "dre" && (
            <div style={{ display: "grid", gap: 18 }}>
              {!dre ? (
                <EmptyState text="Carregue a DRE para visualizar os grupos e contas." />
              ) : (
                dre.groups.map((group) => (
                  <div
                    key={group.group}
                    style={{
                      border: "1px solid #e2e8f0",
                      borderRadius: 18,
                      padding: 18,
                      display: "grid",
                      gap: 12,
                    }}
                  >
                    <div
                      style={{
                        display: "flex",
                        justifyContent: "space-between",
                        alignItems: "center",
                        flexWrap: "wrap",
                        gap: 12,
                      }}
                    >
                      <div>
                        <h3
                          style={{
                            margin: 0,
                            fontSize: 20,
                            fontWeight: 700,
                            textTransform: "capitalize",
                          }}
                        >
                          {group.group}
                        </h3>
                        <p style={{ margin: "4px 0 0", color: "#64748b" }}>
                          Contas do grupo
                        </p>
                      </div>

                      <div
                        style={{
                          background: "#f1f5f9",
                          borderRadius: 999,
                          padding: "8px 14px",
                          fontWeight: 700,
                        }}
                      >
                        {money(group.amount)}
                      </div>
                    </div>

                    <div style={{ overflowX: "auto" }}>
                      <table style={tableStyle}>
                        <thead>
                          <tr>
                            <th style={thStyle}>Código</th>
                            <th style={thStyle}>Conta</th>
                            <th style={{ ...thStyle, textAlign: "right" }}>
                              Valor
                            </th>
                          </tr>
                        </thead>
                        <tbody>
                          {group.accounts.map((account) => (
                            <tr key={`${group.group}-${account.account_code}`}>
                              <td style={tdStyle}>{account.account_code}</td>
                              <td style={tdStyle}>{account.account_name}</td>
                              <td style={{ ...tdStyle, textAlign: "right" }}>
                                {money(account.amount)}
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                ))
              )}
            </div>
          )}

          {activeTab === "balancete" && (
            <div>
              {!trialBalance ? (
                <EmptyState text="Carregue o balancete para visualizar débitos e créditos por conta." />
              ) : (
                <div style={{ overflowX: "auto" }}>
                  <table style={tableStyle}>
                    <thead>
                      <tr>
                        <th style={thStyle}>Código</th>
                        <th style={thStyle}>Conta</th>
                        <th style={{ ...thStyle, textAlign: "right" }}>
                          Débito
                        </th>
                        <th style={{ ...thStyle, textAlign: "right" }}>
                          Crédito
                        </th>
                      </tr>
                    </thead>
                    <tbody>
                      {trialBalance.lines.map((line) => (
                        <tr key={`${line.account_code}-${line.account_name}`}>
                          <td style={tdStyle}>{line.account_code}</td>
                          <td style={tdStyle}>{line.account_name}</td>
                          <td style={{ ...tdStyle, textAlign: "right" }}>
                            {money(line.total_debit)}
                          </td>
                          <td style={{ ...tdStyle, textAlign: "right" }}>
                            {money(line.total_credit)}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          )}

          {activeTab === "graficos" && (
            <div
              style={{
                display: "grid",
                gridTemplateColumns: "1fr 1fr",
                gap: 16,
              }}
            >
              <div style={{ ...cardStyle, padding: 16, height: 360 }}>
                <h3 style={sectionTitleStyle}>Resumo financeiro</h3>
                <div style={{ height: 300, marginTop: 16 }}>
                  {barData.length === 0 ? (
                    <EmptyState text="Carregue a DRE para exibir o gráfico." />
                  ) : (
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={barData}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="name" />
                        <YAxis />
                        <Tooltip formatter={(value: number) => money(value)} />
                        <Bar dataKey="value" radius={[12, 12, 0, 0]} />
                      </BarChart>
                    </ResponsiveContainer>
                  )}
                </div>
              </div>

              <div style={{ ...cardStyle, padding: 16, height: 360 }}>
                <h3 style={sectionTitleStyle}>Composição por grupo</h3>
                <div style={{ height: 300, marginTop: 16 }}>
                  {pieData.length === 0 ? (
                    <EmptyState text="Carregue a DRE para exibir o gráfico." />
                  ) : (
                    <ResponsiveContainer width="100%" height="100%">
                      <PieChart>
                        <Pie
                          data={pieData}
                          dataKey="value"
                          nameKey="name"
                          outerRadius={110}
                          label
                        >
                          {pieData.map((_, index) => (
                            <Cell key={index} />
                          ))}
                        </Pie>
                        <Tooltip formatter={(value: number) => money(value)} />
                      </PieChart>
                    </ResponsiveContainer>
                  )}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function MetricCard({
  icon,
  label,
  value,
}: {
  icon: React.ReactNode;
  label: string;
  value: string;
}) {
  return (
    <div style={{ ...cardStyle, padding: 20 }}>
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: 8,
          color: "#475569",
          fontSize: 14,
          marginBottom: 10,
        }}
      >
        {icon}
        <span>{label}</span>
      </div>
      <div style={{ fontSize: 30, fontWeight: 800 }}>{value}</div>
    </div>
  );
}

function TabButton({
  active,
  onClick,
  label,
}: {
  active: boolean;
  onClick: () => void;
  label: string;
}) {
  return (
    <button
      onClick={onClick}
      style={{
        height: 40,
        padding: "0 18px",
        borderRadius: 999,
        border: active ? "1px solid #0f172a" : "1px solid #cbd5e1",
        background: active ? "#0f172a" : "#fff",
        color: active ? "#fff" : "#0f172a",
        fontWeight: 600,
        cursor: "pointer",
      }}
    >
      {label}
    </button>
  );
}

function EmptyState({ text }: { text: string }) {
  return (
    <div
      style={{
        height: 220,
        border: "1px dashed #cbd5e1",
        borderRadius: 16,
        display: "grid",
        placeItems: "center",
        color: "#64748b",
        textAlign: "center",
        padding: 20,
      }}
    >
      {text}
    </div>
  );
}

function buttonStyle(background: string, color = "#ffffff"): React.CSSProperties {
  return {
    height: 46,
    borderRadius: 14,
    border: background === "#ffffff" ? "1px solid #cbd5e1" : "none",
    background,
    color,
    padding: "0 16px",
    fontWeight: 700,
    display: "flex",
    alignItems: "center",
    gap: 8,
    cursor: "pointer",
  };
}

const tableStyle: React.CSSProperties = {
  width: "100%",
  borderCollapse: "collapse",
};

const thStyle: React.CSSProperties = {
  textAlign: "left",
  padding: "12px 14px",
  borderBottom: "1px solid #e2e8f0",
  color: "#475569",
  fontSize: 13,
};

const tdStyle: React.CSSProperties = {
  padding: "12px 14px",
  borderBottom: "1px solid #f1f5f9",
  fontSize: 14,
};