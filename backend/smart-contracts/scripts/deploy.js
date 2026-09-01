const hre = require("hardhat");

async function main() {
  console.log("Deploying smart contracts...");

  // Deploy IdentityManager
  const IdentityManager = await hre.ethers.getContractFactory("IdentityManager");
  const identityManager = await IdentityManager.deploy();
  await identityManager.deployed();
  console.log("IdentityManager deployed to:", identityManager.address);

  // Deploy AssetManager
  const AssetManager = await hre.ethers.getContractFactory("AssetManager");
  const assetManager = await AssetManager.deploy();
  await assetManager.deployed();
  console.log("AssetManager deployed to:", assetManager.address);

  // Deploy AccessControlManager
  const AccessControlManager = await hre.ethers.getContractFactory("AccessControlManager");
  const accessControl = await AccessControlManager.deploy();
  await accessControl.deployed();
  console.log("AccessControlManager deployed to:", accessControl.address);

  // Deploy AuditTrail
  const AuditTrail = await hre.ethers.getContractFactory("AuditTrail");
  const auditTrail = await AuditTrail.deploy();
  await auditTrail.deployed();
  console.log("AuditTrail deployed to:", auditTrail.address);

  // Save addresses
  const addresses = {
    identityManager: identityManager.address,
    assetManager: assetManager.address,
    accessControl: accessControl.address,
    auditTrail: auditTrail.address,
    network: hre.network.name,
    deploymentTime: new Date().toISOString()
  };

  const fs = require("fs");
  fs.writeFileSync(
    "deployment-addresses.json",
    JSON.stringify(addresses, null, 2)
  );

  console.log("\nDeployment complete!");
  console.log("Addresses saved to deployment-addresses.json");
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
