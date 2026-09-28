import { useEffect, useState } from "react";
import axios from "axios";
import "./App.css";

const API = "http://localhost:8000";

function App() {
  const [scenario, setScenario] = useState(1);
  const [sku, setSku] = useState("MILK-001");
  const [proposedQuantity, setProposedQuantity] = useState(800);
  const [data, setData] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadData("MILK-001");
  }, []);

  const scenarios = {
    1: {
      sku: "MILK-001",
      quantity: 800
    },
    2: {
      sku: "RICE-001",
      quantity: 500
    }
  };

  const selectScenario = async (value) => {
    const selected = scenarios[value];

    setScenario(value);
    setSku(selected.sku);
    setProposedQuantity(selected.quantity);
    setResult(null);

    await loadData(selected.sku);
  };

  const loadData = async (productSku) => {
    try {
      const response = await axios.get(
        `${API}/purchasing/${productSku}`
      );
      setData(response.data);
    } catch (error) {
      console.error(error);
    }
  };

  const resetScenario = async () => {
    setLoading(true);
    setResult(null);

    try {
      await axios.post(`${API}/scenarios/reset/${scenario}`);
      await loadData(scenarios[scenario].sku);
    } catch (error) {
      console.error(error);
    }

    setLoading(false);
  };

  const reviewPurchase = async () => {
    setLoading(true);
    setResult(null);

    try {
      const response = await axios.post(
        `${API}/agent/review/${sku}?purchase_quantity=${proposedQuantity}`
      );

      setResult({
        type: "review",
        ...response.data
      });
    } catch (error) {
      console.error(error);
    }

    setLoading(false);
  };

  const executePurchase = async () => {
    setLoading(true);
    setResult(null);

    try {
      const response = await axios.post(
        `${API}/agent/purchase/${sku}?purchase_quantity=${proposedQuantity}`
      );

      setResult({
        type: "execution",
        ...response.data
      });

      await loadData(sku);
    } catch (error) {
      console.error(error);
    }

    setLoading(false);
  };

  const decision = result?.decision;

  return (
    <div className="app">
      <header>
        <div>
          <h1>ProcureAI</h1>
          <p>AI-powered purchasing decision system</p>
        </div>

        <div className="status">
          <span></span>
          Backend connected
        </div>
      </header>

      <main>
        <section className="scenario-bar">
          <div>
            <label>Scenario</label>

            <select
              value={scenario}
              onChange={(e) => selectScenario(Number(e.target.value))}
            >
              <option value={1}>
                Purchase Recommendation Review
              </option>
              <option value={2}>
                Supplier Cannot Fulfil
              </option>
            </select>
          </div>

          <button
            className="secondary"
            onClick={resetScenario}
            disabled={loading}
          >
            Reset Scenario
          </button>
        </section>

        {data && (
          <>
            <section className="product-header">
              <div>
                <span className="label">PRODUCT</span>
                <h2>{data.product.name}</h2>
                <p>{data.product.sku}</p>
              </div>

              <div className="proposed">
                <span className="label">PROPOSED PURCHASE</span>
                <strong>{proposedQuantity} units</strong>
              </div>
            </section>

            <section className="cards">
              <div className="card">
                <span className="label">INVENTORY</span>
                <strong>{data.inventory.quantity}</strong>
                <p>units on hand</p>
              </div>

              <div className="card">
                <span className="label">FORECAST</span>
                <strong>{data.forecast.expected_demand}</strong>
                <p>expected demand</p>
              </div>

              <div className="card">
                <span className="label">OPEN PO</span>
                <strong>
                  {data.open_po?.quantity || 0}
                </strong>
                <p>units incoming</p>
              </div>

              <div className="card">
                <span className="label">BUDGET</span>
                <strong>
                  ₹{data.constraints.budget.toLocaleString()}
                </strong>
                <p>available</p>
              </div>
            </section>

            <section className="panel">
              <div className="panel-title">
                <h3>Supplier Information</h3>
              </div>

              <div className="suppliers">
                {data.suppliers.map((supplier) => (
                  <div
                    className="supplier"
                    key={supplier.id}
                  >
                    <div>
                      <strong>{supplier.name}</strong>
                      <span>
                        Supplier #{supplier.id}
                      </span>
                    </div>

                    <div>
                      <span>Available</span>
                      <strong>
                        {supplier.available_quantity}
                      </strong>
                    </div>

                    <div>
                      <span>MOQ</span>
                      <strong>{supplier.moq}</strong>
                    </div>

                    <div>
                      <span>Price</span>
                      <strong>₹{supplier.unit_price}</strong>
                    </div>

                    <div>
                      <span>Lead time</span>
                      <strong>
                        {supplier.lead_time_days} days
                      </strong>
                    </div>
                  </div>
                ))}
              </div>
            </section>

            <section className="actions">
              <button
                className="primary"
                onClick={reviewPurchase}
                disabled={loading}
              >
                {loading ? "Analyzing..." : "Review Purchase"}
              </button>

              <button
                className="execute"
                onClick={executePurchase}
                disabled={loading || !result}
              >
              Execute Purchase
            </button>
            </section>

            {result && (
              <section className="result">
                <div className="result-header">
                  <div>
                    <span className="label">AI DECISION</span>
                    <h2>{decision?.decision}</h2>
                  </div>

                  <div className="quantity">
                    {decision?.recommended_quantity} units
                  </div>
                </div>

                <div className="reason">
                  <h3>Reasoning</h3>
                  <p>{decision?.reason}</p>
                </div>

                <div className="evidence">
                  <h3>Evidence</h3>

                  {decision?.evidence?.map(
                    (item, index) => (
                      <div
                        className="evidence-item"
                        key={index}
                      >
                        <span>✓</span>
                        <p>{item}</p>
                      </div>
                    )
                  )}
                </div>

                {result.validation && (
                  <div className="validation">
                    <div>
                      <span>Business validation</span>
                      <strong>
                        {result.validation.valid
                          ? "✓ Passed"
                          : "✕ Failed"}
                      </strong>
                    </div>

                    {result.validation.total_cost !==
                      undefined && (
                      <div>
                        <span>Total cost</span>
                        <strong>
                          ₹
                          {result.validation.total_cost.toLocaleString()}
                        </strong>
                      </div>
                    )}

                    {result.validation.projected_inventory !==
                      undefined && (
                      <div>
                        <span>Projected inventory</span>
                        <strong>
                          {result.validation.projected_inventory}
                        </strong>
                      </div>
                    )}
                  </div>
                )}

                {result.execution && (
                  <div className="execution">
                    <div>
                      <span>Execution</span>
                      <strong>
                        {result.execution.success
                          ? "✓ Successful"
                          : "✕ Failed"}
                      </strong>
                    </div>

                    {result.execution.purchase_order_id && (
                      <div>
                        <span>Purchase Order</span>
                        <strong>
                          #{result.execution.purchase_order_id}
                        </strong>
                      </div>
                    )}

                    {result.execution.supplier && (
                      <div>
                        <span>Supplier</span>
                        <strong>
                          {result.execution.supplier}
                        </strong>
                      </div>
                    )}

                    {result.execution.quantity && (
                      <div>
                        <span>Quantity</span>
                        <strong>
                          {result.execution.quantity}
                        </strong>
                      </div>
                    )}
                  </div>
                )}

                {result.post_validation && (
                  <div className="success">
                    <span>✓</span>
                    <div>
                      <strong>
                        {result.post_validation.status}
                      </strong>
                      <p>
                        {result.post_validation.reason}
                      </p>
                    </div>
                  </div>
                )}
              </section>
            )}
          </>
        )}
      </main>
    </div>
  );
}

export default App;