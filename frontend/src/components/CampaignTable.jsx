export default function CampaignTable({ campaigns }) {
  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr><th>Campaign</th><th>Spend</th><th>Revenue</th><th>ROAS</th><th>CAC</th><th>Orders</th></tr>
        </thead>
        <tbody>
          {campaigns.map((campaign) => (
            <tr key={campaign.campaign_id}>
              <td><strong>{campaign.campaign_id}</strong></td>
              <td>${campaign.spend.toFixed(2)}</td>
              <td>${campaign.attributed_revenue.toFixed(2)}</td>
              <td>{campaign.roas.toFixed(2)}x</td>
              <td>${campaign.cac.toFixed(2)}</td>
              <td>{campaign.conversions}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
