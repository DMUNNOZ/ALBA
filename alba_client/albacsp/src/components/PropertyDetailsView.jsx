import React from 'react';
import './PropertyDetailsView.css';

const PropertyDetails = () => {
  return (
    <div className="property-details-info">
      <div className="property-section-info">
        <h2>Security</h2>
        <p>The optimization of security focuses on two key factors: minimizing the average impact and minimizing the size of the CWE set.</p>
        <div className="property-item-info security-info">
          <strong>Average Impact:</strong>
          <p>The average impact is calculated based on the individualized impacts of each device selected in the configuration. Each impact linked to a device is the result of calculating the weighted average of the base values from the Common Vulnerability Scoring System (CVSS) standard for the set of associated potential vulnerabilities.</p>
        </div>
        <div className="property-item-info security-info">
          <strong>CWE Set:</strong>
          <p>On the other hand, the CWE set indicates the diversity of potential weaknesses present in the resulting configuration. This set is populated with each CWE found in the list of potential vulnerabilities associated with the selected devices.</p>
        </div>
      </div>
      
      <div className="property-section-info">
        <h2>Usability</h2>
        <div className="property-item-info usability-info">
          <p>The usability property reflects the number of applications required to manage the set of devices in the resulting configuration. Given the importance of centralized management, a configuration is considered better when fewer applications are needed to control it.</p>
          <table className="property-table-info">
            <thead>
              <tr>
                <th>Usability Level</th>
                <th>Description</th>
              </tr>
            </thead>
            <tbody>
            <tr>
                <td>Poor</td>
                <td>More than 3 apps</td>
              </tr>
              <tr>
                <td>Good</td>
                <td>Between 1 and 3 apps</td>
              </tr>
              <tr>
                <td>Excellent</td>
                <td>No app required</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div className="property-section-info">
        <h2>Connectivity</h2>
        <div className="property-item-info connectivity-info">
          <p>The connectivity property indicates the different communication technologies present in the resulting configuration. Configurations with a greater number of distinct connectivity technologies are considered superior.</p>
          <table className="property-table-info">
            <thead>
              <tr>
                <th>Connectivity Level</th>
                <th>Description</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>Low</td>
                <td>Less than 3 different connectivity technologies</td>
              </tr>
              <tr>
                <td>Medium</td>
                <td>Between 3 and 5 different connectivity technologies</td>
              </tr>
              <tr>
                <td>High</td>
                <td>More than 5 different connectivity technologies</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div className="property-section-info">
        <h2>Sustainability</h2>
        <p>Maximizing sustainability aims to find the configuration that achieves the highest average sustainability score.</p>
        <div className="property-item-info sustainability-info">
          <strong>Average Sustainability:</strong>
          <p>The average sustainability property is calculated based on the sustainability values associated with the devices that make up the resulting configuration. The individual sustainability value of each device is determined by its internal characteristics, including its computational capacity and the type of energy source it uses for operation.</p>
          <table className="property-table-info">
            <thead>
              <tr>
                <th>Sustainability Level</th>
                <th>Description</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>Low</td>
                <td>Less than 4</td>
              </tr>
              <tr>
                <td>Medium</td>
                <td>Between 4 and 8</td>
              </tr>
              <tr>
                <td>High</td>
                <td>More than 8</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

export default PropertyDetails;



