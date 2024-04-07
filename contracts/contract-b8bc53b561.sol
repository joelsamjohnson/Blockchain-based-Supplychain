// SPDX-License-Identifier: MIT
pragma solidity >=0.4.22 <0.9.0;

contract TextileSupplyChain {
    address public Owner;

    constructor() public {
        Owner = msg.sender;
    }

    modifier onlyByOwner() {
        require(msg.sender == Owner);
        _;
    }

    enum STAGE {
        Init,
        RawMaterialSupply,
        Manufacture,
        Distribution,
        Retail,
        Sold
    }

    uint256 public productCtr = 0;
   //Raw material supplier count
    uint256 public rmsCtr = 0;
    //Manufacturer count
    uint256 public manCtr = 0;
    //distributor count
    uint256 public disCtr = 0;
    //retailer count
    uint256 public retCtr = 0;

    struct Product {
        uint256 id;
        string name;
        string description;
        uint256 RMSid;
        uint256 MANid;
        uint256 DISid;
        uint256 RETid;
        STAGE stage;
    }

    mapping(uint256 => Product) public ProductStock;

    struct rawMaterialSupplier {
        address addr;
        uint256 id;
        string name;
        string place;
    }

    mapping(uint256 => rawMaterialSupplier) public RMS;

    struct manufacturer {
        address addr;
        uint256 id;
        string name;
        string place;
    }

    mapping(uint256 => manufacturer) public MAN;

    struct distributor {
        address addr;
        uint256 id;
        string name;
        string place;
    }

    mapping(uint256 => distributor) public DIS;

    struct retailer {
        address addr;
        uint256 id;
        string name;
        string place;
    }

    mapping(uint256 => retailer) public RET;

//To add raw material suppliers. Only contract owner can add a new raw material supplier
    function addRMS(
        address _address,
        string memory _name,
        string memory _place
    ) public onlyByOwner() {
        rmsCtr++;
        RMS[rmsCtr] = rawMaterialSupplier(_address, rmsCtr, _name, _place);
    }

    //To add manufacturer. Only contract owner can add a new manufacturer
    function addManufacturer(
        address _address,
        string memory _name,
        string memory _place
    ) public onlyByOwner() {
        manCtr++;
        MAN[manCtr] = manufacturer(_address, manCtr, _name, _place);
    }

    //To add distributor. Only contract owner can add a new distributor
    function addDistributor(
        address _address,
        string memory _name,
        string memory _place
    ) public onlyByOwner() {
        disCtr++;
        DIS[disCtr] = distributor(_address, disCtr, _name, _place);
    }

    //To add retailer. Only contract owner can add a new retailer
    function addRetailer(
        address _address,
        string memory _name,
        string memory _place
    ) public onlyByOwner() {
        retCtr++;
        RET[retCtr] = retailer(_address, retCtr, _name, _place);
    }
    
    //To supply raw materials from RMS supplier to the manufacturer
    function RMSsupply(uint256 _productID) public {
        require(_productID > 0 && _productID <= productCtr);
        uint256 _id = findRMS(msg.sender);
        require(_id > 0);
        require(ProductStock[_productID].stage == STAGE.Init);
        ProductStock[_productID].RMSid = _id;
        ProductStock[_productID].stage = STAGE.RawMaterialSupply;
}

    //To check if RMS is available in the blockchain
    function findRMS(address _address) private view returns (uint256) {
        require(rmsCtr > 0);
        for (uint256 i = 1; i <= rmsCtr; i++) {
            if (RMS[i].addr == _address) return RMS[i].id;
        }
        return 0;
    }

    //To manufacture product
    function Manufacturing(uint256 _productID) public {
        require(_productID > 0 && _productID <= productCtr);
        uint256 _id = findMAN(msg.sender);
        require(_id > 0);
        require(ProductStock[_productID].stage == STAGE.RawMaterialSupply);
        ProductStock[_productID].MANid = _id;
        ProductStock[_productID].stage = STAGE.Manufacture;
    }

    //To check if Manufacturer is available in the blockchain
    function findMAN(address _address) private view returns (uint256) {
        require(manCtr > 0);
        for (uint256 i = 1; i <= manCtr; i++) {
            if (MAN[i].addr == _address) return MAN[i].id;
        }
        return 0;
    }

    //To supply products from Manufacturer to distributor
    function Distribute(uint256 _productID) public {
        require(_productID > 0 && _productID <= productCtr);
        uint256 _id = findDIS(msg.sender);
        require(_id > 0);
        require(ProductStock[_productID].stage == STAGE.Manufacture);
        ProductStock[_productID].DISid = _id;
        ProductStock[_productID].stage = STAGE.Distribution;
    }

    //To check if distributor is available in the blockchain
    function findDIS(address _address) private view returns (uint256) {
        require(disCtr > 0);
        for (uint256 i = 1; i <= disCtr; i++) {
            if (DIS[i].addr == _address) return DIS[i].id;
        }
        return 0;
    }

    //To supply products from distributor to retailer
    function Retail(uint256 _productID) public {
        require(_productID > 0 && _productID <= productCtr);
        uint256 _id = findRET(msg.sender);
        require(_id > 0);
        require(ProductStock[_productID].stage == STAGE.Distribution);
        ProductStock[_productID].RETid = _id;
        ProductStock[_productID].stage = STAGE.Retail;
    }

    //To check if retailer is available in the blockchain
    function findRET(address _address) private view returns (uint256) {
        require(retCtr > 0);
        for (uint256 i = 1; i <= retCtr; i++) {
            if (RET[i].addr == _address) return RET[i].id;
        }
        return 0;
    }

    //To sell products from retailer to consumer
    function Sold(uint256 _productID) public {
        require(_productID > 0 && _productID <= productCtr);
        uint256 _id = findRET(msg.sender);
        require(_id > 0);
        require(_id == ProductStock[_productID].RETid); //Only correct retailer can mark product as sold
        require(ProductStock[_productID].stage == STAGE.Retail);
        ProductStock[_productID].stage = STAGE.Sold;
    }

    // To add new products to the stock
    function addproduct(string memory _name, string memory _description)
        public
        onlyByOwner()
    {
        require((rmsCtr > 0) && (manCtr > 0) && (disCtr > 0) && (retCtr > 0));
        productCtr++;
        ProductStock[productCtr] = Product(
            productCtr,
            _name,
            _description,
            0,
            0,
            0,
            0,
            STAGE.Init
        );
    }
    // Implementation details for sharding, sidechains, and off-chain solutions would depend on specific requirements and technical decisions based on the broader ecosystem and infrastructure available for scaling Ethereum-based applications.

    // Note: Implementing sharding, sidechains, and off-chain solutions involves advanced concepts and is beyond the scope of this contract example. They generally require integration with external systems or services and detailed architectural design.
    //To show status to client applications
    function showStage(uint256 _productID)
        public
        view
        returns (string memory)
    {
        require(productCtr > 0, "No products in the system.");
        if (ProductStock[_productID].stage == STAGE.Init)
            return "Product Initialized";
        else if (ProductStock[_productID].stage == STAGE.RawMaterialSupply)
            return "Raw Material Supply Stage";
        else if (ProductStock[_productID].stage == STAGE.Manufacture)
            return "Manufacturing Stage";
        else if (ProductStock[_productID].stage == STAGE.Distribution)
            return "Distribution Stage";
        else if (ProductStock[_productID].stage == STAGE.Retail)
            return "Retail Stage";
        else if (ProductStock[_productID].stage == STAGE.Sold)
            return "Product Sold";
        else
            return "Unknown Stage";
    }

}
